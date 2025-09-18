# processamento_imagens

Pacote faz parte do desafio de criar um pacote de processamento de imagem

## Instalação


# Pacote de processamento simples de imagem

Pacote que faz parte da atividade da [DigitalOneInnovation](dio.me) de criar um pacote de processamento de imagem simples.
Repositório: [desafiodio-pacote](https://github.com/mochiemi/desafios-dio/desafiodio-pacote)

## Instalação
```bash
pip  install  auladio_criandopacotes
```
## Utilizando o código

### Importando os módulos do pacote
	from auladio_criandopacotes.functions import equalize, grayscale
	from auladio_criandopacotes.tools import io, plot
### Tabela de funções
| Função | Módulo | Descrição | Dependência |
|--|--|--|--|
| `io.read_image('caminho_da_imagem\\arquivo_imagem.jpg')` | `tools` | Necessário para ler uma imagem de um diretório para ser processada no código. | `scikit-image` |
|`io.save_image(imagem, caminho)`| `tools` |Retorna a imagem no caminho indicado. | `scikit-image` |
| `plot.plot_result(imagem1, imagem2,...,*args, nome):` | `tools` | Recebe um número *args de imagens para serem plotadas | `matplotlib` |
|`io.save_image(imagem, caminho)`| `tools` |Retorna a imagem no caminho indicado|  `scikit-image` |
|`equalize.equalizing(imagem)`| `functions` |Equaliza os canais de cores RGB da imagem|  `scikit-image` |
|`grayscale.grayscaling(imagem)`|`functions`|Faz com que a imagem fique em escala-cinza| `scikit-image` |

### Código Teste
Disponível neste [source](https://github.com/mochiemi/desafios-dio/desafiodio-pacote/teste)
## Autora
Tiemi Suyama
Email: tiemi.suyama@gmail.com
Github:  https://github.com/mochiemi/

## License

[MIT](https://choosealicense.com/licenses/mit/)