from PIL import Image
import base64

def get_image_base64(image_path):
    """
        Função para converter imagem local para base64'
    """    
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
def load_css():
    """
        Função para carregar Arquivo CSS
    """    
    try:
        with open("/style/header.css") as f:
            return f.read()
    except FileNotFoundError:
        return "/* CSS file not found */"
def header_page():
    """
        Função para retornae o cabeçalho da página
    """    
    logo_pag = get_image_base64("./imgs/EMConsult.png")
    return f"""
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: -60px; margin-bottom: -5px;">
            <h3 style="font-weight: bold; color: #000080; line-height: 1;">Gestão de Operações</h3>      
    </div>
    <hr style="margin-top: -10px; margin-bottom: 10px; border: 1px solid #ccc;">
    """  
def header_side():
    """
        Função para retornar o cabeçalho da barra lateral
    """    
    return f"""
        <div>
            <h3 class="header_side">GEOP Gerência Operacional</h3>
            <p class="header_side">Aplicando IA no sistema OPTIMUS</p>        
             <hr class="hr">
        </div>
    """    
def footer_page():
    return """
    <div class="footer">
        <p>© 2025, GEOP Todos os direitos reservados.</p>
    </div>
    """

def sidebar_component():
    return """
    <div class="sidebar">
        <h4>Menu</h4>
        <ul>
            <li><a href="#">Item 1</a></li>
            <li><a href="#">Item 2</a></li>
            <li><a href="#">Item 3</a></li>
        </ul>
    </div>
    """


        #with st.sidebar:
    #    with st.spinner("Loading..."):
    #        time.sleep(5)
