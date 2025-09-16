#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from .engine import Engine
from .state import get_thread_id, set_thread_id, kb_ids, add_kb_ids, get_multimodal_thread_info, update_multimodal_thread, clear_multimodal_thread, cleanup_old_multimodal_threads, get_multimodal_thread_id, get_thread_content_summary
from .tools import unified, extract_between, extract_urls_from_response, function_tools

app = typer.Typer(add_completion=False)
console = Console()
eng = Engine()

# ---------- ASK (Enhanced with Unified Engine) ----------
@app.command("ask")
def ask(
    prompt: str = typer.Argument(..., help="Your question/instruction."),
    model: str = typer.Option(None, "--model", "-m"),
    thread: Optional[str] = typer.Option(None, "--thread", "-t", help="Thread name to maintain context."),
    stream: bool = typer.Option(False, "--stream", "-s", help="Stream tokens as they arrive"),
    system: Optional[str] = typer.Option(None, "--system", help="Optional system instructions."),
    use_multimodal_engine: bool = typer.Option(True, "--multimodal/--legacy", help="Use unified multimodal engine (recommended).")
):
    """Ask a text question with optional threading. Now uses unified multimodal engine by default."""
    
    if use_multimodal_engine:
        # Use new unified multimodal engine for consistent Responses API usage
        try:
            # Get multimodal thread info (backward compatible with text threads)
            prev_response_id = get_multimodal_thread_id(thread) if thread else None
            if not prev_response_id and thread:
                # Try legacy text thread ID for backward compatibility
                prev_response_id = get_thread_id(thread)
            
            resp = eng.analyze_multimodal_content(
                content_path=None,  # Text-only
                user_prompt=prompt,
                system_prompt=system,
                model=model,
                previous_response_id=prev_response_id,
                content_type="text"
            )
            
            # Display response
            if hasattr(resp, 'output') and resp.output:
                content = resp.output[0].content[0].text
                console.print(Markdown(content))
            else:
                console.print(Markdown(getattr(resp, 'output_text', str(resp))))
            
            # Update thread state
            if getattr(resp, "id", None) and thread:
                model_used = getattr(resp, 'model', model or eng.model_default)
                update_multimodal_thread(thread, resp.id, "text", model_used)
                # Also update legacy thread for backward compatibility
                set_thread_id(resp.id, thread)
                
        except Exception as e:
            console.print(f"[red]Error with multimodal engine: {e}[/red]")
            console.print("[yellow]Falling back to legacy engine...[/yellow]")
            use_multimodal_engine = False
    
    if not use_multimodal_engine:
        # Legacy engine path (original implementation)
        prev = get_thread_id(thread)
        resp = eng.send(
            input=prompt,
            model=model,
            instructions=system,
            previous_response_id=prev,
            stream=stream
        )
        if not stream:
            console.print(Markdown(resp.output_text))
        if getattr(resp, "id", None):
            set_thread_id(resp.id, thread)

# ---------- RESEARCH (web_search) ----------
@app.command("research")
def research(
    query: str = typer.Argument(...),
    bullets: int = typer.Option(6, "--bullets", "-b"),
    model: str = typer.Option("gpt-4o", "--model", "-m"),
    as_json: bool = typer.Option(False, "--json", help="Return JSON instead of markdown"),
    stream: bool = typer.Option(False, "--stream", "-s"),
):
    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "ResearchSummary",
            "schema": {
                "type": "object",
                "properties": {
                    "bullets": {"type": "array", "items": {"type": "string"}},
                    "sources": {"type": "array", "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string", "format": "uri"}
                        },
                        "required": ["url"],
                        "additionalProperties": False
                    }},
                    "risks_unknowns": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["bullets", "sources"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

    prompt = (
        f"Summarize the latest on: {query}\n"
        f"- Output {bullets} terse bullets.\n"
        f"- Use bracketed citations inline.\n"
        f"- End with 'Risks & Unknowns'."
    )
    kwargs = dict(
        input=prompt, model=model,
        tools=[{"type": "web_search"}],
        stream=stream
    )
    if as_json:
        kwargs["response_format"] = schema

    resp = eng.send(**kwargs)
    if as_json:
        data = json.loads(resp.output_text)
        console.print_json(data=data)
    else:
        console.print(Panel.fit(Markdown(resp.output_text), title="Summary"))
        urls = extract_urls_from_response(resp)
        if urls:
            console.print("\n[bold]Sources[/bold]")
            for i, (title, url) in enumerate(urls, 1):
                console.print(f"{i}. {(title + ' — ') if title else ''}{url}")

# ---------- KB INDEX / KB RESEARCH (file_search) ----------
@app.command("kb-index")
def kb_index(folder: Path = typer.Argument(..., exists=True, file_okay=False)):
    from .state import get_kb_vector_store_id, set_kb_vector_store_id
    
    count = 0
    ids = []
    
    # Upload files
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".pdf", ".py", ".rst"}:
            fid = eng.upload_for_kb(p)
            ids.append(fid); count += 1
    
    if not ids:
        console.print("[yellow]No files found to index.[/yellow]")
        return
    
    # Create or get vector store
    vector_store_id = get_kb_vector_store_id()
    if not vector_store_id:
        console.print("[blue]Creating new vector store...[/blue]")
        vector_store_id = eng.create_vector_store("edge-assistant-kb")
        set_kb_vector_store_id(vector_store_id)
    
    # Add files to vector store
    console.print(f"[blue]Adding {len(ids)} files to vector store...[/blue]")
    eng.add_files_to_vector_store(vector_store_id, ids)
    
    # Still store individual file IDs for backward compatibility
    add_kb_ids(ids)
    console.print(f"[green]Indexed {count} files ({len(ids)} new).[/green]")

@app.command("kb-list")
def kb_list():
    """List files in the knowledge base."""
    from .state import get_kb_vector_store_id
    
    files = kb_ids()
    vector_store_id = get_kb_vector_store_id()
    
    if not files and not vector_store_id:
        console.print("[yellow]No knowledge base found. Run: edge-assistant kb-index ./docs[/yellow]")
        return
    
    console.print(f"[blue]Knowledge Base Status:[/blue]")
    console.print(f"  File IDs: {len(files)} files")
    console.print(f"  Vector Store: {vector_store_id or 'None'}")
    
    if files:
        console.print(f"\n[blue]Indexed Files (by ID):[/blue]")
        for i, fid in enumerate(files, 1):
            console.print(f"  {i}. {fid}")

@app.command("kb-research")
def kb_research(
    query: str = typer.Argument(...),
    model: str = typer.Option("gpt-4o", "--model", "-m"),
    stream: bool = typer.Option(False, "--stream", "-s"),
):
    files = kb_ids()
    if not files:
        raise typer.Exit("No KB files. Run: edge-assistant kb-index ./docs")

    # Get vector store ID from state - we need to update kb-index to create vector stores
    from .state import get_kb_vector_store_id
    vector_store_id = get_kb_vector_store_id()
    
    if not vector_store_id:
        console.print("[red]Error: No vector store found. Please re-run kb-index to create one.[/red]")
        raise typer.Exit(1)
    
    resp = eng.send(
        model=model,
        input=f"Answer using the provided knowledge files. Cite sources clearly. Q: {query}",
        tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
        stream=stream,
    )
    if not stream:
        console.print(Markdown(resp.output_text))

# ---------- EDIT ----------
@app.command("edit")
def edit(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, resolve_path=True),
    instruction: str = typer.Argument(..., help="Describe the change you want."),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m"),
    apply: bool = typer.Option(False, "--apply", help="Write changes to disk"),
    backup: bool = typer.Option(True, "--backup/--no-backup"),
):
    original = path.read_text(encoding="utf-8")
    sys_prompt = (
        "You are a precise editor. Produce the FULL new file content only.\n"
        "Wrap it strictly between <BEGIN_FILE> and <END_FILE>."
    )
    user_prompt = (
        f"File: {path.name}\nInstruction: {instruction}\n\n"
        f"--- ORIGINAL START ---\n{original}\n--- ORIGINAL END ---"
    )
    resp = eng.send(
        model=model,
        instructions=sys_prompt,
        input=user_prompt,
    )
    text = resp.output_text
    new_content = extract_between(text, "<BEGIN_FILE>", "<END_FILE>") or text.strip()
    diff = unified(original, new_content, str(path))

    if not diff:
        console.print("[green]No changes proposed.[/green]")
        return

    console.print(Syntax(diff, "diff", theme="ansi_dark", word_wrap=True))
    if apply:
        if backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_text(original, encoding="utf-8")
            console.print(f"[dim]Backup -> {bak}[/dim]")
        path.write_text(new_content, encoding="utf-8")
        console.print("[bold green]Applied.[/bold green]")
    else:
        console.print("[yellow]Dry run. Use --apply to write changes.[/yellow]")

# ---------- AGENT (optional tool calls with guardrails) ----------
@app.command("agent")
def agent(task: str, approve: bool = typer.Option(False, "--approve")):
    resp = eng.send(
        model="gpt-4o-mini",
        instructions="You may call tools to modify files. Prefer minimal diffs and safe paths.",
        input=task,
        tools=function_tools(),
    )
    acted = False
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) == "function_call" and item.name == "fs_write":
            args = json.loads(item.arguments)
            p = Path(args["path"]).expanduser().resolve()
            before = p.read_text(encoding="utf-8") if p.exists() else ""
            diff = unified(before, args["content"], str(p))
            console.print(Syntax(diff, "diff", theme="ansi_dark"))
            if approve:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(args["content"], encoding="utf-8")
                console.print(f"[green]Wrote {p}[/green]")
            else:
                console.print("[yellow]Dry run. Re-run with --approve to apply.[/yellow]")
            acted = True
    if not acted:
        console.print(Markdown(getattr(resp, "output_text", "")))

# ---------- UNIFIED MULTIMODAL ANALYSIS ----------
@app.command("analyze")
def analyze(
    prompt: str = typer.Argument(..., help="Your question or instruction about the content."),
    content_path: Optional[Path] = typer.Option(None, "--file", "-f", exists=True, dir_okay=False, resolve_path=True,
                                                help="Path to content file (image, audio, video, document). Leave empty for text-only."),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System/developer prompt for analysis context."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use (auto-selected based on content type)."),
    thread: Optional[str] = typer.Option(None, "--thread", "-t", help="Thread name to maintain context across interactions."),
    content_type: str = typer.Option("auto", "--type", help="Content type: auto, text, image, audio, video, file."),
    max_interactions: int = typer.Option(20, "--max-interactions", help="Maximum interactions per thread (default: 20)."),
    clear_thread: bool = typer.Option(False, "--clear-thread", help="Clear the specified thread before analysis."),
    save: Optional[str] = typer.Option(None, "--save", help="Save output to a new file (provide filename or use 'auto' for automatic naming).")
):
    """Unified analysis command supporting text, images, audio, video, and files with threading."""
    try:
        # Auto-cleanup old threads
        cleanup_old_multimodal_threads()
        
        # Handle thread clearing
        if clear_thread and thread:
            if clear_multimodal_thread(thread):
                console.print(f"[green]Cleared thread '{thread}'[/green]")
            else:
                console.print(f"[yellow]Thread '{thread}' does not exist[/yellow]")
            return
        
        # Determine content type and path
        content_path_str = str(content_path) if content_path else None
        
        if thread:
            # Threaded analysis with context
            thread_info = get_multimodal_thread_info(thread)
            
            # Check interaction limits
            if thread_info["total_interactions"] >= max_interactions:
                console.print(f"[red]Thread '{thread}' has reached max interactions ({max_interactions}). Use --clear-thread to reset.[/red]")
                raise typer.Exit(1)
            
            prev_response_id = get_multimodal_thread_id(thread)
            
            # Show thread status
            if thread_info["total_interactions"] > 0:
                summary = get_thread_content_summary(thread)
                console.print(f"[dim]Thread '{thread}': {summary}[/dim]")
            
            # Call unified multimodal analysis
            result = eng.analyze_multimodal_content(
                content_path=content_path_str,
                user_prompt=prompt,
                system_prompt=system,
                model=model,
                previous_response_id=prev_response_id,
                content_type=content_type
            )
            
            # Update thread state with detected content type
            detected_type = content_type if content_type != "auto" else eng._detect_content_type(content_path_str) if content_path_str else "text"
            model_used = getattr(result, 'model', model or eng.model_default)
            
            if getattr(result, "id", None):
                update_multimodal_thread(thread, result.id, detected_type, model_used)
                
        else:
            # Fresh context analysis
            result = eng.analyze_multimodal_content(
                content_path=content_path_str,
                user_prompt=prompt,
                system_prompt=system,
                model=model,
                previous_response_id=None,
                content_type=content_type
            )
        
        # Extract and display result
        output_text = getattr(result, 'output_text', None)
        if not output_text and hasattr(result, 'output') and result.output:
            # Handle Responses API output format
            output_text = result.output[0].content[0].text if result.output[0].content else str(result)
        elif not output_text:
            output_text = str(result)

        # Save to file if requested
        if save and content_path:
            if save == "auto":
                # Auto-generate filename based on original file
                original_stem = content_path.stem
                original_dir = content_path.parent
                save_path = original_dir / f"{original_stem}_converted.md"
            else:
                # Use provided filename in the same directory as the input file
                save_path = content_path.parent / save

            try:
                save_path.write_text(output_text, encoding="utf-8")
                console.print(f"[green]Output saved to: {save_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving file: {e}[/red]")

        # Display result
        console.print(Markdown(output_text))
        
    except NotImplementedError as e:
        console.print(f"[yellow]Feature not yet available: {e}[/yellow]")
        raise typer.Exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        raise typer.Exit(1)

# ---------- LEGACY IMAGE ANALYSIS (for backward compatibility) ----------
@app.command("analyze-image")
def analyze_image_legacy(
    image_path: Path = typer.Argument(..., exists=True, dir_okay=False, resolve_path=True),
    prompt: str = typer.Argument(..., help="Description of what you want to analyze in the image."),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System/developer prompt for analysis context."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Vision model to use."),
    thread: Optional[str] = typer.Option(None, "--thread", "-t", help="Thread name to maintain context across images."),
    max_images: int = typer.Option(5, "--max-images", help="Maximum images per thread (default: 5)."),
    clear_thread: bool = typer.Option(False, "--clear-thread", help="Clear the specified thread before analysis.")
):
    """Legacy: Analyze an image. Use 'analyze' command instead for unified multimodal support."""
    console.print("[yellow]Note: 'analyze-image' is deprecated. Use 'edge-assistant analyze' for full multimodal support.[/yellow]")
    
    # Convert max_images to max_interactions (images are just one type of interaction now)
    max_interactions = max_images * 4  # Allow more interactions since we support mixed content
    
    # Redirect to unified analyze command
    try:
        analyze(
            content_path=image_path,
            prompt=prompt,
            system=system,
            model=model,
            thread=thread,
            content_type="image",
            max_interactions=max_interactions,
            clear_thread=clear_thread
        )
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[red]Error analyzing image: {e}[/red]")
        raise typer.Exit(1)

def main():
    app()

if __name__ == "__main__":
    main()
