from PIL import Image
import base64


# Função para converter imagem local para base64
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# HTML Header Páginas


line_space = f"""
    <div style="margin-top: 15px;" >
    </div>
"""    

logo_pag = get_image_base64("./imgs/casapark.png")
header_page = f"""
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: -50px; margin-bottom: -10px;">
    <img src="data:image/png;base64,{logo_pag}" 
         style="width: 120px; height: auto;">
    <div>
        <h4 style="font-weight: bold; color: #4682B4; line-height: 1;">Gestão de Ordens de Serviços</h4>      
    </div>
</div>
<hr style="margin-top: -10px; margin-bottom: 5px; border: 1px solid #ccc;">
"""    

# HTML Header Sidebar
#logo_side = get_image_base64("./imgs/EMConsult.png")
header_side = f"""
    <div >
        <h3 style="margin-top: -35px; color: #696969; text-align: center;">GEOP Gerência Operacional</b></h3>
        <p style="margin-top: -20px; color: #696969; text-align: center;">Aplicando IA no sistema OPTIMUS</b></p>        
        <hr style="margin-top: -15px; border: 1px solid #ccc;">    
    </div>
"""    

def widget(texto1, texto2, texto3):

    return (f"""
                <div style="height: 105px; margin-bottom: 5px; background-color: #F19B08; border-radius: 5px; border: 1px solid gray; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    padding: 5px; display: flex; flex-direction: column;">
                    <span style="font-size: 22px; color: black; text-align: left;  margin: 0; line-height: 1.2"><strong>{texto1}</strong></span>
                    <span style="font-size: 36px; color: darkblue; text-align: center; font-weight: bold; margin-top: 5px; line-height: 1.2">{texto2}</span>
                    <span style="font-size: 12px; color: white; text-align: center; margin-top: 5px; line-height: 1.2">{texto3}</span>        
                </div>
            """)


