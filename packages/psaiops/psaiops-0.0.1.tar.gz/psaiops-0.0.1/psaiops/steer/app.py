import gradio

# MODEL ########################################################################

def create_model_tab():
    pass

# PROMPT #######################################################################

# SAMPLING #####################################################################

class GradioInterface:
    """Manages the Gradio user interface."""
    
    def __init__(self, orchestra: LLMForestOrchestra):
        """Initialize the interface."""
        self.orchestra = orchestra
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(title="LLM Forest Orchestra", theme=gr.themes.Soft()) as demo:
            gr.Markdown(self.DESCRIPTION)
            
            with gr.Tabs():
                with gr.TabItem("🎵 Generate Music"):
                    self._create_generation_tab()
            
            return demo
    
    def _create_generation_tab(self):
        """Create the main generation tab."""
        with gr.Row():
            with gr.Column(scale=1):
                text_input = gr.Textbox(
                    value=self.EXAMPLE_TEXT,
                    label="Input Text",
                    lines=8,
                    placeholder="Enter text to sonify..."
                )
                
                model_name = gr.Textbox(
                    value=self.orchestra.DEFAULT_MODEL,
                    label="Hugging Face Model",
                    info="Model must support output_hidden_states and output_attentions"
                )
                
                compute_mode = gr.Radio(
                    choices=["Full model", "Mock latents"],
                    value="Mock latents",
                    label="Compute Mode",
                    info="Mock latents for quick CPU-only demo"
                )
                
                with gr.Row():
                    instrument_preset = gr.Dropdown(
                        choices=self.orchestra.instrument_manager.list_presets(),
                        value="Ensemble (melody+bass+pad etc.)",
                        label="Instrument Preset"
                    )
                    
                    scale_choice = gr.Dropdown(
                        choices=self.orchestra.scale_manager.list_scales() + ["Custom"],
                        value="C pentatonic",
                        label="Musical Scale"
                    )
                
                custom_scale = gr.Textbox(
                    value="",
                    label="Custom Scale Notes",
                    placeholder="60,62,65,67,70",
                    visible=False
                )
                
                with gr.Row():
                    base_tempo = gr.Slider(
                        120, 960,
                        value=480,
                        step=1,
                        label="Tempo (ticks per beat)"
                    )
                    
                    num_layers = gr.Slider(
                        1, 6,
                        value=6,
                        step=1,
                        label="Max Layers"
                    )
                
                with gr.Row():
                    velocity_low = gr.Slider(
                        1, 126,
                        value=40,
                        step=1,
                        label="Min Velocity"
                    )
                    
                    velocity_high = gr.Slider(
                        2, 127,
                        value=90,
                        step=1,
                        label="Max Velocity"
                    )
                
                seed = gr.Number(
                    value=42,
                    precision=0,
                    label="Random Seed"
                )
                
                generate_btn = gr.Button(
                    "🎼 Generate MIDI",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=1):
                midi_output = gr.File(
                    label="Generated MIDI File",
                    file_types=[".mid", ".midi"]
                )
                
                stats_display = gr.Markdown(label="Quick Stats")
                
                metadata_json = gr.Code(
                    label="Metadata (JSON)",
                    language="json"
                )
                
                with gr.Row():
                    play_instructions = gr.Markdown(
                        """
                        ### 🎧 How to Play
                        1. Download the MIDI file
                        2. Open in any DAW or MIDI player
                        3. Adjust instruments and effects as desired
                        4. Export to audio format
                        """
                    )
        
        # Set up interactions
        def update_custom_scale_visibility(choice):
            return gr.update(visible=(choice == "Custom"))
        
        scale_choice.change(
            update_custom_scale_visibility,
            inputs=[scale_choice],
            outputs=[custom_scale]
        )
        
        def generate_wrapper(
            text, model_name, compute_mode, base_tempo,
            velocity_low, velocity_high, scale_choice,
            custom_scale, num_layers, instrument_preset, seed
        ):
            """Wrapper for generation with error handling."""
            try:
                # Parse custom scale if needed
                custom_notes = None
                if scale_choice == "Custom" and custom_scale:
                    custom_notes = [int(x.strip()) for x in custom_scale.split(",")]
                
                # Generate
                filename, metadata = self.orchestra.generate(
                    text=text,
                    model_name=model_name,
                    compute_mode=compute_mode,
                    base_tempo=int(base_tempo),
                    velocity_range=(int(velocity_low), int(velocity_high)),
                    scale_name=scale_choice,
                    custom_scale_notes=custom_notes,
                    num_layers=int(num_layers),
                    instrument_preset=instrument_preset,
                    seed=int(seed)
                )
                
                # Format stats
                stats = metadata.get("stats", {})
                stats_text = f"""
                ### Generation Statistics
                - **Layers Used**: {stats.get('num_layers', 'N/A')}
                - **Tokens Processed**: {stats.get('num_tokens', 'N/A')}
                - **Total Notes**: {stats.get('total_notes', 'N/A')}
                - **Notes per Layer**: {stats.get('notes_per_layer', [])}
                - **Scale**: {stats.get('scale', [])}
                - **Tempo**: {stats.get('tempo_ticks_per_beat', 'N/A')} ticks/beat
                """
                
                return filename, stats_text, json.dumps(metadata, indent=2)
                
            except Exception as e:
                error_msg = f"### ❌ Error\n{str(e)}"
                return None, error_msg, json.dumps({"error": str(e)}, indent=2)
        
        generate_btn.click(
            fn=generate_wrapper,
            inputs=[
                text_input, model_name, compute_mode, base_tempo,
                velocity_low, velocity_high, scale_choice,
                custom_scale, num_layers, instrument_preset, seed
            ],
            outputs=[midi_output, stats_display, metadata_json]
        )