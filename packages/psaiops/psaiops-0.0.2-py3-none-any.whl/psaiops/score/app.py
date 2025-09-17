import gradio

# META #########################################################################

TITLE = '''Token Scoring'''
INTRO = '''Score each input / output token according to a given metric.'''
STYLE = ''''''

# MODEL ########################################################################

def create_model_tab() -> None:
    pass

# ROOT #########################################################################

def create_root_block(title: str=TITLE, intro: str=INTRO, style: str=STYLE) -> gradio.Block:
    with gradio.Blocks(theme=gradio.themes.Soft(), title=title, css=style) as __app:
        with gradio.Row():
            with gradio.Column(scale=1):
                gradio.Markdown(intro)
        return __app

# MAIN #########################################################################

if __name__ == '__main__':
    __app = create_root_block()
    __app.launch(share=True, debug=True)