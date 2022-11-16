from PIL import Image

Img1 = Image.open('img1.png')
Img2 = Image.open('img2.png')
Img3 = Image.open('img3.png')
Img4 = Image.open('img4.png')
Img5 = Image.open('img5.png')
Img6 = Image.open('img6.png')
Img7 = Image.open('img7.png')
Img8 = Image.open('img8.png')

vect_image=[Img1, Img2, Img3, Img4, Img5, Img6, Img7, Img8]

def merge_image(img_vector, image_size):

    if len(img_vector) == 0:
        return

    img_vector = [elem.resize((image_size, image_size)) for elem in img_vector]

    res_image = Image.new('RGB',(len(img_vector) * image_size, image_size), (255,255,255))

    for i in range(len(img_vector)):
        res_image.paste(img_vector[i], (i * image_size, 0))

    res_image.save("new_image.jpg","JPEG")

merge_image(vect_image, 256)