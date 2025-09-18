import matplotlib.pyplot as plt

def plot_result(*args, nome):
    number_images = len(args)
    fig, axis = plt.subplots(nrows=1, ncols = number_images, figsize=(12, 4))
    names_lst = ['Imagem {}'.format(i) for i in range(0, number_images)]
    print(f'{nome.title()}')
    for ax, name, image in zip(axis, names_lst, args):
        ax.set_title(name)
        ax.imshow(image, cmap='gray')
        ax.axis('off')
    fig.tight_layout()
    plt.show()