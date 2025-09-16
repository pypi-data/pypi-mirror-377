# Imprint — Documentação (Português / English)

> Esta documentação contém versões em **Português (PT-BR)** e **English (EN)** do README e guias rápidos para a biblioteca **Imprint**.

---

# Português (PT-BR)

## Imprint

**Imprint** é uma biblioteca Python para criação e geração programática de templates visuais (certificados, crachás, convites e outros), com campos dinâmicos que podem ser preenchidos a partir de APIs, planilhas, bancos de dados ou qualquer fonte de dados.

### ⚡ Principais recursos

* Criação de **templates personalizados** com múltiplas páginas.
* Campos dinâmicos: **texto**, **imagem** e **QR code** (e mais tipos no futuro).
* Definição de **posição, tamanho e dimensões** para cada campo em uma página.
* Exportação para **imagens PNG** e suporte planejado para PDF e outros formatos.
* Integração fácil com **APIs, Excel/CSV e bancos de dados**.
* Arquitetura modular para facilitar adição de novos tipos de campos e motores de render (engines).

### 🚀 Instalação

Quando publicado no PyPI:

```bash
pip install imprintlab
```

Para instalar diretamente do repositório durante desenvolvimento:

```bash
pip install git+https://github.com/danieldevpy/imprint.git
```

### 📝 Exemplo rápido (usage)

```python
import os
from imprint import Model

# Cria um modelo simples com uma página e campos dinâmicos
def criar_cracha_basico():
    # caminho do fundo
    caminho_fundo = os.path.join(os.getcwd(), "examples/assets/badge.jpeg")

    # cria modelo
    modelo = Model.new(name="Cracha-Basico")

    # cria página da frente
    pagina_frente = modelo.new_page(name="frente").set_background(caminho_fundo)

    # adiciona campo de texto: nome
    pagina_frente.add_component(name="Nome Completo", component="text", form_key="nome")\
        .set_position((520, 320)).set_size(24)

    # adiciona campo de texto: cargo
    pagina_frente.add_component(name="Cargo", component="text", form_key="cargo")\
        .set_position((510, 400)).set_size(24)

    # adiciona campo de texto: função
    pagina_frente.add_component(name="Função", component="text", form_key="funcao")\
        .set_position((610, 480)).set_size(24)

    # adiciona campo de imagem: foto
    pagina_frente.add_component(name="Foto", component="img", form_key="foto")\
        .set_position((35, 245)).set_dimension((360, 360))

    return modelo

modelo = criar_cracha_basico()

dados_formulario = {
    "nome": "Daniel Fernandes Pereira",
    "cargo": "Desenvolvedor de Software",
    "funcao": "Administrador",
    "foto": os.path.join(os.getcwd(), "examples/assets/photo.png"),
}

# Construir e renderizar
resultado = modelo.build_img(dados_formulario)

# Visualizar no visualizador padrão do sistema
resultado.show()
```

> Observações:
>
> * `Model.new(...)` cria um novo template.
> * `Page` aceita background por caminho de arquivo; caso não use imagem, especifique `width` e `height`.
> * `form_key` associa o componente a uma chave no dicionário `form_data` passado ao `build_...()`.

### 🔧 Estrutura da API (resumo)

### Model | Modelo
* `Model.new(name: str)` → Cria uma nova instância de `Model` com o nome fornecido.
* `Model.new_page(name: str)` → Cria uma nova `Page` e a vincula ao `Model` pai.
* `Model.get_form()` → Retorna um único dicionário combinando todos os forms de todas as páginas.
* `Model.get_schema()` → Retorna um dicionário com nomes das páginas como chaves e seus forms como valores.
* `Model.export(path: str)` → Salva a estrutura do model em um arquivo JSON.
* `Model.load(path: str)` → Método de classe para carregar um model de um arquivo JSON.

### Page | Pagina
* `Page.add_component(name: str, component: str, form_key: Optional[str])` → Adiciona um componente (Text ou Img) à página.
* `Page.get_component(name: str)` → Retorna o componente associado ao nome do campo.
* `Page.set_width(width: int)` → Define a largura da página.
* `Page.set_height(height: int)` → Define a altura da página.
* `Page.set_dimension(width: int, height: int)` → Define largura e altura.
* `Page.set_background(background: Union[str, Tuple[int,int,int]])` → Define a imagem ou cor de fundo.

### Component | Componente
* `Text` → Representa componentes de texto. Métodos: `get_color()`, `get_size()`, `get_position()`, `get_value()`, `get_dimension_r()`, `get_font()`, `set_color()`, `set_size()`, `set_position()`, `set_value()`, `set_dimension_r()`, `set_font()`
* `Img` → Representa componentes de imagem. Métodos: `get_position()`, `get_dimension()`, `get_path()`, `set_position()`, `set_dimension()`, `set_path()`, `set_value()`

### Builder / Renderização

* `BuilderMixin.build_img(forms)` → Retorna um `ImageBuild` com as imagens renderizadas.
* Métodos: `to_images()`, `to_image()`, `to_bytes(page: Optional[int])`, `save(path: str)`, `show(page: Optional[int])`

### 📌 Boas práticas e dicas

* Use `Component` com `form_key` para ligar os campos ao seu dicionário de dados.
* Para imagens, sempre passe caminhos de arquivo válidos ou URIs locais; cuide do tamanho e proporção.
* Ao usar fundo sem imagem, defina `width` e `height` na página para evitar erro.

### 🌟 Contribuições

1. Fork no GitHub.
2. Crie um branch: `git checkout -b feature/nome-da-feature`.
3. Abra um PR com descrição clara do que foi feito.

### 📄 Licença

MIT License © Daniel Fernandes

---

# English (EN)

## Imprint

**Imprint** is a Python library to programmatically create and generate visual templates (certificates, badges, invitations, etc.) with dynamic fields that can be filled from APIs, spreadsheets, databases or any data source.

### ⚡ Features

* Create **custom templates** with multiple pages.
* Dynamic fields: **text**, **image** and **QR code** (more field types planned).
* Define **position, size and dimension** for each field on a page.
* Export to **PNG images**; PDF and other export formats are planned.
* Easy integration with **APIs, Excel/CSV and databases**.
* Modular engine/architecture to allow new render engines and field types.

### 🚀 Installation

When published on PyPI:

```bash
pip install imprintlab
```

To install from the Git repository (development):

```bash
pip install git+https://github.com/danieldevpy/imprint.git
```

### 📝 Quickstart example

```python
import os
from imprint import Model

# Build a simple badge template with dynamic fields
def create_basic_badge():
    # Getting background image path
    background_path = os.path.join(os.getcwd(), "examples/assets/badge.jpeg")
    
    # Creating basic model
    model = Model.new(name="Basic-Badge")

    # Creating front page
    front_page = model.new_page(name="front")\
        .set_background(background_path)

    # Adding text field: name
    front_page.add_component(name="Full Name", component="text", form_key="name")\
        .set_position((520, 320))\
        .set_size(24)  # defining component properties

    # Adding text field: job
    front_page.add_component(name="Job", component="text", form_key="job")\
        .set_position((510, 400))\
        .set_size(24)  # defining component properties

    # Adding text field: role
    front_page.add_component(name="Role", component="text", form_key="role")\
        .set_position((610, 480))\
        .set_size(24)  # defining component properties

    # Adding image field: photo
    front_page.add_component(name="Photo", component="img", form_key="photo")\
        .set_position((35, 245))\
        .set_dimension((360, 360))  # defining component properties

    return model

model = create_basic_badge()

form_data = {
    "name": "Daniel Fernandes Pereira",
    "job": "Software Developer",
    "role": "Administrator",
    "photo": os.path.join(os.getcwd(), "examples/assets/photo.png")
}

# Build and render (Pillow engine by default)
result = model.build(form_data).render()

# Build and render
result = model.build_img(form_data)

# Display in the system's default viewer
result.show()
```

### 🔧 API Structure (summary)

#### Model

* `Model.new(name: str)` → Creates a new `Model` instance with the given name.
* `Model.new_page(name: str)` → Creates a new `Page` and links it to the parent `Model`.
* `Model.get_form()` → Returns a single dictionary combining all forms from all pages.
* `Model.get_schema()` → Returns a dictionary with page names as keys and their forms as values.
* `Model.export(path: str)` → Saves the model structure to a JSON file.
* `Model.load(path: str)` → Class method to load a model from a JSON file.

#### Page

* `Page.add_component(name: str, component: str, form_key: Optional[str])` → Adds a component (Text or Img) to the page.
* `Page.get_component(name: str)` → Returns the component associated with the field name.
* `Page.set_width(width: int)` → Sets the page width.
* `Page.set_height(height: int)` → Sets the page height.
* `Page.set_dimension(width: int, height: int)` → Sets width and height.
* `Page.set_background(background: Union[str, Tuple[int,int,int]])` → Sets the background image or color.

#### Component

* `Text` → Represents text components. Methods: `get_color()`, `get_size()`, `get_position()`, `get_value()`, `get_dimension_r()`, `get_font()`, `set_color()`, `set_size()`, `set_position()`, `set_value()`, `set_dimension_r()`, `set_font()`
* `Img` → Represents image components. Methods: `get_position()`, `get_dimension()`, `get_path()`, `set_position()`, `set_dimension()`, `set_path()`, `set_value()`

#### Builder / Rendering

* `BuilderMixin.build_img(forms)` → Returns an `ImageBuild` with rendered images.
* Methods: `to_images()`, `to_image()`, `to_bytes(page: Optional[int])`, `save(path: str)`, `show(page: Optional[int])`

### 📌 Best Practices & Tips

* Use `Component` with `form_key` to link fields to your data dictionary.
* For images, always provide valid file paths or local URIs; handle size and proportion carefully.
* When using a background without an image, set `width` and `height` on the page to avoid errors.

### 🌟 Contributions

1. Fork on GitHub.
2. Create a branch: `git checkout -b feature/feature-name`.
3. Open a PR with a clear description of your changes.

### 📄 License

MIT License © Daniel Fernandes
