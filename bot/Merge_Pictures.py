from PIL import Image

# vect_image=[Img1, Img2, Img3, Img4, Img5, Img6, Img7, Img8] vect_imag.append(Img1)

def merge_image(img_vector, image_size = 256):

    if len(img_vector) == 0:
        return

    img_vector = [elem.resize((image_size, image_size)) for elem in img_vector]

    res_image = Image.new('RGB', (len(img_vector) * image_size, image_size), (47, 49, 54))

    for i in range(len(img_vector)):
        res_image.paste(img_vector[i], (i * image_size, 0))

    res_image.save("images/job_picture.png")

# merge_image(vect_image)
