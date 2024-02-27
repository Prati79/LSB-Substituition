from PIL import Image
from numpy import array
import numpy as np
import math


def decimalToBinary(n):
    return "{0:08b}".format(int(n))


def binaryToDecimal(n):
    return int(n, 2)


def numberOfPixelsNeeded(binarySecretData, bit, imgType):
    numOfPixels = 0
    if imgType == 'L':
        numOfPixels = math.ceil(len(binarySecretData)/bit)
    else:
        numOfPixels = math.ceil(len(binarySecretData)/(3*bit))
    return numOfPixels


def PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if (mse == 0):
        return 100
    max_pixel = 255.0
    psnr = 10 * math.log10(max_pixel**2 / mse)
    return psnr


def encodeGrayImage(coverImage, secretData, bits):

    pixel_array = array(coverImage)
    binarySecretData = ""
    # Adding Delimiter to decode the message
    secretData += "$##$"
    for letter in secretData:
        binarySecretData += decimalToBinary(ord(letter))
    pixels_required = numberOfPixelsNeeded(
        binarySecretData, bits, coverImage.mode)
    pixel_counter = 0

    if pixels_required > pixel_array.size:
        print("Secret Message Can't be embedded as size of Cover Image is small")
        return
    else:
        embeddedSecretDataLen = 0
        # row
        for i in range(coverImage.width):
            # col
            for j in range(coverImage.height):
                if pixel_counter < pixels_required:
                    binaryPixelVal = decimalToBinary(pixel_array[i][j])
                    changedPixelValue = binaryPixelVal[:(-bits)] + \
                        binarySecretData[embeddedSecretDataLen:embeddedSecretDataLen+2]
                    pixel_array[i][j] = binaryToDecimal(changedPixelValue)
                    embeddedSecretDataLen += 2
                    pixel_counter += 1

    stegoImage = Image.fromarray(pixel_array)
    stegoImage.save('{}stego.png'.format(
        coverImage.filename.split('.')[0]))
    PSNRValue = PSNR(array(coverImage), pixel_array)
    print("PSNR value is : {}".format(PSNRValue))
    return stegoImage


def decodeImage(stegoImage, bits):
    pixel_array = array(stegoImage)
    binarySecretData = ""
    if stegoImage.mode == 'L':
        print("\nGrayscale Image")
    else:
        print("\nRGB Image")
    for values in pixel_array:
        for pixels in values:
            if stegoImage.mode == 'L':
                binaryPixelVal = decimalToBinary(pixels)
                binarySecretData += binaryPixelVal[-bits:]
            elif stegoImage.mode == 'RGB':
                for x in pixels:
                    binaryPixelVal = decimalToBinary(x)
                    binarySecretData += binaryPixelVal[-bits:]

    embeddedSecretData = ""
    for i in range(0, len(binarySecretData)-1, 8):
        temp = binaryToDecimal(binarySecretData[i:i+8])
        embeddedSecretData += chr(temp)
        if embeddedSecretData[-4:] == "$##$":
            break

    return embeddedSecretData[:-4]


def encodeRGBImage(coverImage, secretData, bits):
    pixel_array = array(coverImage)
    binarySecretData = ""
    # Adding Delimiter to decode the message
    secretData += "$##$"
    for letter in secretData:
        binarySecretData += decimalToBinary(ord(letter))
    pixels_required = numberOfPixelsNeeded(
        binarySecretData, bits, coverImage.mode)
    pixel_counter = 0
    if pixels_required > pixel_array.size:
        print("Secret Message Can't be embedded as size of Cover Image is small")
        return
    else:
        embeddedSecretDataLen = 0
        for values in pixel_array:
            for pixel in values:
                if pixel_counter < pixels_required and embeddedSecretDataLen < len(binarySecretData):
                    for x in range(len(pixel)):
                        binaryPixelVal = decimalToBinary(pixel[x])
                        changedPixelValue = binaryPixelVal[:(
                            -bits)] + binarySecretData[embeddedSecretDataLen:embeddedSecretDataLen+2]
                        pixel[x] = binaryToDecimal(changedPixelValue)
                        embeddedSecretDataLen += 2
                    pixel_counter += 1

    stegoImage = Image.fromarray(pixel_array)
    stegoImage.save('{}stegoImageRGB.png'.format(
        coverImage.filename.split('.')[0]))
    PSNRValue = PSNR(array(coverImage), pixel_array)
    print("PSNR value is : {}".format(PSNRValue))
    return stegoImage


if __name__ == '__main__':

    bits = 2
    print(
        "What would you like to do? \n 1.Encode Data into Image \n 2.Decode an Image \n")
    option = int(input("Your Choice : "))
    if option == 1:
        img = input("Enter image name(with extension) : ")
        image = Image.open(img)
        data = input("Enter data to be encoded : ")
        if (len(data) == 0):
            raise ValueError('Data is empty')
        print("\n********* For {} *************".format(img))
        if image.mode == 'L':
            print("\nGrayScale Image")
            print("\nEncoding...")
            encodeGrayImage(image, data, bits)
        elif image.mode == 'RGB':
            print("\nRGB Image")
            print("\nEncoding...")
            encodeRGBImage(image, data, bits)
    elif option == 2:
        img = input("Enter image name(with extension) : ")
        image = Image.open(img)
        print("\nDecoding...")
        print("\nEmbedded Secret Message is  :" +
              decodeImage(image, bits) + "\n")
