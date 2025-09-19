# 🎨 ImgAdjust: Transferência de Cores e Brilho para Imagens

Um pacote Python simples e eficiente para aplicar correspondência de histogramas, permitindo transferir o estilo de cores, brilho e contraste de uma imagem de referência para uma imagem de origem.

## ✨ Funcionalidades

- Realiza correspondência de histogramas de forma eficiente.
- Permite transferir características visuais entre imagens.
- Salva a imagem processada em um arquivo especificado.

---

## 🚀 Instalação

Você pode instalar o pacote `package_histmatch` diretamente com o `pip`:

```bash
pip install package_histmatch
```

# 🛠️ Como usar

Para utilizar as funcionalidades do pacote, importe a função match_images e chame-a no seu script com os caminhos das imagens que deseja processar.

```Python
from package_histmatch import match_images

# Exemplo de uso:
# match_images(caminho_da_origem, caminho_da_referencia, caminho_de_saida)
match_images("images/modern2.jpg", "images/retro3.jpg", "images/resultado_final.jpg")

```

Parâmetros da função match_images:

- source_path: Caminho para a imagem que terá seu histograma ajustado (imagem de origem).

- reference_path: Caminho para a imagem com o histograma a ser copiado (imagem de referência).

- output_path: Caminho completo onde a imagem resultante será salva.

---

# 🖼️ Exemplo Visual
A seguir, um exemplo da aplicação do pacote, transformando uma imagem moderna com a paleta de cores de uma imagem retrô:

![Capa do Projeto - Imagem Correspondida](imagens/result_histogram.jpg) 

🤝 Contribuições
Sinta-se à vontade para abrir issues ou enviar pull requests se tiver sugestões ou encontrar bugs!

👩‍💻 Autor
- Nayara

- GitHub: https://github.com/Nayarah

## 📄 Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
