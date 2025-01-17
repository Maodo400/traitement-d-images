from PIL import Image
from math import sqrt
from math import log
from math import fabs

def comparaisonHisto3channels(histoA, histoB, factor):
    resultsBatta = [comparaisonHistoBhattacharyya(histoA[c], histoB[c]) for c in range(3)]
    moyenneBatta = sum(resultsBatta) / 3
    return round(moyenneBatta * 100, 2)


def comparaisonHisto(histoA, histoB, factor):
    resultsBatta = comparaisonHistoBhattacharyyaHSV(histoA, histoB)
    return round(resultsBatta * 100, 2)


def comparaisonImage3channels(im1, im2, facteur):
    newIm1, newIm2 = normalize([im1, im2])
    histo1 = buildHistogram(newIm1)
    histo2 = buildHistogram(newIm2)
    return comparaisonHisto3channels(histo1, histo2, facteur)


def buildHistogram(im):
    pix = im.load()
    if im.mode == "RGB":
        R, G, B = ([0] * 256 for _ in range(3))
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                r, g, b = pix[i, j]
                R[r] += 1
                G[g] += 1
                B[b] += 1
        return R, G, B
    
    elif im.mode == "HSV":
        H, S, V = [0] * 360, [0] * 100, [0] * 100
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                h, s, v = pix[i, j]
                H[h] += 1
                S[s] += 1
                V[v] += 1
        return H, S, V
    
    else:
        raise ValueError("Image mode must be RGB or HSV")


def maxValeur(histo):
    return max(max(channel) for channel in histo)


def drawBin(im, startx, endx, value, maxV, channel):
    pix = im.load()
    hauteur = (value * im.size[1]) / maxV
    for i in range(startx, endx):
        for j in range(511, 513 - int(hauteur), -1):
            val = list(pix[i, j])
            val[channel] = 255
            pix[i, j] = tuple(val)


def drawHistogram(histo):
    newIm = Image.new("RGB", (512, 512))
    maxV = maxValeur(histo)
    for j, channel_index in zip(range(0, 256), range(3)):
        for x_offset in range(3):
            drawBin(newIm, j * 2, j * 2 + 1, histo[channel_index][j], maxV, channel_index)
    return newIm



def toGray(im):
    if im.mode == "RGB":
        gray = Image.new("L", im.size)
        pix = im.load()
        gpix = gray.load()
        for i in range(0, im.size[0]):
            for j in range(0, im.size[1]):
                val = pix[i, j]
                gpix[i, j] = int((val[0]+val[1]+val[2])/3)
        return gray
    else:
        return im


def sobel(im):
    pix = im.load()
    result = Image.new("L", im.size)
    rpix = result.load()
    for i in range(1, im.size[0] - 1):
        for j in range(1, im.size[1] - 1):
            a = -pix[i - 1, j - 1] - 2*pix[i - 1, j] - pix[i - 1, j + 1]
            b = pix[i + 1, j - 1] + 2*pix[i + 1, j] + pix[i + 1, j + 1]
            c = -pix[i - 1, j - 1] - 2*pix[i, j - 1] - pix[i + 1, j - 1]
            d = pix[i + 1, j + 1] + 2*pix[i, j + 1] + pix[i + 1, j + 1]
            gX = a + b
            gY = c + d
            g = int(sqrt((gX*gX)+(gY*gY)).real)
            rpix[i, j] = g
    return result


def normalize(images):
    w = []
    h = []
    for i in images:
        w.append(i.size[0])
        h.append(i.size[1])
    w.sort()
    h.sort()
    if w[0] == w[-1] and h[0] == h[-1]:
        return images
    else:
        newImages = []
        for i in images:
            if i.mode == "L":
                newImages.append(cropGris(i, 0, 0, w[0], h[0]))
            if i.mode == "RGB":
                newImages.append(crop(i, 0, 0, w[0], h[0]))
        newImagesT = tuple(newImages)
        return newImagesT


def diff(a, b):
    newA, newB = normalize([a, b])
    pixA = newA.load()
    pixB = newB.load()
    type(pixA)
    newImage = Image.new("RGB", newA.size)
    pix = newImage.load()
    for i in range(0, newImage.size[0]):
        for j in range(0, newImage.size[1]):
            valA = pixA[i, j]
            valB = pixB[i, j]
            pix[i, j] = (abs(valA[0] - valB[0]),
                         abs(valA[1] - valB[1]),
                         abs(valA[2] - valB[2]))
    return newImage


def normHisto(histo):
    r = []
    s = 0.0
    for h in histo:
        s += h
    for h in histo:
        r.append(h/s)
    return r


def comparaisonHistoBhattacharyya(histoA, histoB):
    hA = normHisto(histoA)
    hB = normHisto(histoB)
    distance = 0.
    for i in range(0, 255):
        distance += (hA[i] * hB[i]) ** 0.5
    newDistance = -log(distance)
    return newDistance


def comparaisonHistoBhattacharyyaHSV(histoA, histoB):
    hA = normHisto(histoA)
    hB = normHisto(histoB)
    distance = 0.
    for i in range(0, 255):
        distance += (hA[i] * hB[i]) ** 0.5
    newDistance = -log(distance)
    return newDistance


def compDifImages(im):
    pix = im.load()
    comp = 0.
    taille = im.size[0]*im.size[1]
    prcentge = 0.
    for x in range(0, im.size[0]):
        valR = []
        valG = []
        valB = []
        for y in range(0, im.size[1]):
            valR = pix[x, y][0]
            valG = pix[x, y][1]
            valB = pix[x, y][2]
            if 0 <= valR <= 32 and 0 <= valG <= 32 and 0 <= valB <= 32:
                comp = comp + 0
            else:
                comp = comp + 1
    prcentge = (comp/taille)*100
    prcentge = round(prcentge, 2)
    return prcentge


def compDifImagesGris(im):
    pix = im.load()
    comp = 0.
    taille = im.size[0]*im.size[1]
    prcentge = 0
    for x in range(0, im.size[0]):
        s = 0
        for y in range(0, im.size[1]):
            s = pix[x, y]
            if 0 <= s <= 15:
                comp = comp + 0
            else:
                comp = comp + 1
    prcentge = (comp/taille)*100
    prcentge = round(prcentge, 2)
    return prcentge


def diffGris(A, B):
    a, b = normalize([A, B])
    pixa = a.load()
    pixb = b.load()
    newIm = Image.new("L", a.size)
    pix1 = newIm.load()
    for i in range(0, newIm.size[0]):
        for j in range(0, newIm.size[1]):
            val1 = pixa[i, j]
            val2 = pixb[i, j]
            val = abs(int(val1) - int(val2))
            pix1[i, j] = val
    return newIm


def crop(im, x, y, w, h):
    pix = im.load()
    newIm = Image.new("RGB", (w, h))
    pix1 = newIm.load()
    for i in range(x, x+w):
        for j in range(y, y + h):
            pix1[i-x, j-y] = pix[i, j]
    return newIm


def cropGris(im, x, y, w, h):
    pix = im.load()
    newIm = Image.new("L", (w, h))
    pix1 = newIm.load()
    for i in range(x, x+w):
        for j in range(y, y + h):
            pix1[i-x, j-y] = pix[i, j]
    return newIm

# def drawPixel(im, x, y, color):
#     pix = im.load()
#     pix[x, y] = color
#
#
# def drawHLine(im, y, color):
#     pix = im.load()
#     for i in range(0, im.size[1], 1):
#         pix[i, y] = color
#
#
# def drawVLine(im, x, color):
#     pix = im.load()
#     for i in range(0, im.size[0], 1):
#         pix[x, i] = color
#
#
# def drawRectangle(im, x, y, w, h, color):
#     pix = im.load()
#     for i in range(x, x+w):
#         for j in range(y, y+h):
#             pix[i, j] = color
#
#
# def increaseValues(im, dec):
#     pix = im.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = pix[i, j]
#             pix[i, j] = (val[0] + dec, val[1] + dec, val[2] + dec)
#
#
# def reverseChannels(im):
#     pix = im.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = pix[i, j]
#             pix[i, j] = (val[2], val[1], val[0])
#
#
# def inverseValues(im):
#     pix = im.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = pix[i, j]
#             pix[i, j] = (255-val[0], 255-val[1], 255-val[2])
#
#
# def buildLookUpTable(start, stop):
#     lut = []
#     for i in range(0, 256):
#         Pi = (i/255.)   # Pourcentage avancement
#         startpi = (1-Pi)
#         lut.append((int(round(start[0]*startpi)) + int(round(stop[0]*Pi)),
#                     int(round(start[1]*startpi)) + int(round(stop[1]*Pi)),
#                     int(round(start[2]*startpi)) + int(round(stop[2]*Pi))))
#     # print(lut)
#     return lut
#
#
# def applyLookUpTable(im, lut):
#     newIm = Image.new("RGB", (im.size[0], im.size[1]))
#     pix = im.load()
#     pix1 = newIm.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = list(pix[i, j])
#             pix1[i, j] = lut[val[0]]
#     return newIm
#
#
# def vFlip(im):
#     pix = im.load()
#     newIm = Image.new("RGB", (im.size[0], im.size[1]))
#     pix1 = newIm.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             pix1[im.size[0]-1-i, im.size[1]-1-j] = pix[i, j]
#     return newIm
#
#
# def hFlip(im):
#     pix = im.load()
#     newIm = Image.new("RGB", (im.size[0], im.size[1]))
#     pix1 = newIm.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             x = fabs(i - im.size[0]-1)
#             if x > im.size[0] - 1:
#                 x = im.size[0] - 1
#             pix1[x, j] = pix[i, j]
#     return newIm
#
#
# def rotate(im):
#     pix = im.load()
#     newIm = Image.new("RGB", (im.size[1], im.size[0]))
#     pix1 = newIm.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = pix[i, j]
#             pix1[im.size[1]-1-j, im.size[0]-1-i] = val
#     return newIm
#
#
# def translate(im, dec):
#     pix = im.load()
#     newIm = Image.new("RGB", (im.size[0], im.size[1]))
#     pix1 = newIm.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             decI = i + dec[0]
#             decJ = j + dec[1]
#             if(decI > newIm.size[0]):
#                 decI = decI - newIm.size[0]
#             if(decJ > newIm.size[1]):
#                 decJ = decJ - newIm.size[1]
#             if(decI < newIm.size[0] and decJ < newIm.size[1]):
#                 pix1[decI, decJ] = pix[i, j]
#     return newIm
#
#
# def zoom(im, factor):
#     pix = im.load()
#     newIm = Image.new("RGB", (im.size[0] * factor, im.size[1] * factor))
#     pix1 = newIm.load()
#     for i in range(0, im.size[0]*factor):
#         for j in range(0, im.size[1]*factor):
#             pix1[i, j] = pix[i/factor, j/factor]
#     return newIm
#
#
# def zoomAndCrop(im, factor):
#     newIm = zoom(im, factor)
#     newIm2 = crop(newIm, (newIm.size[0]-im.size[0])/2,
#                         (newIm.size[1]-im.size[1])/2, im.size[0], im.size[1])
#     return newIm2
#
#
# def blur(im, radius):
#     pix = im.load()
#     result = Image.new("L", im.size)
#     rpix = result.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             somme = 0
#             count = 0
#             for k in range(i - radius, i + radius+1):
#                 for l in range(j - radius, j + radius+1):
#                     kOut = (k < 0) or (k > im.size[0] - 1)
#                     lOut = (l < 0) or (l > im.size[1] - 1)
#                     if kOut or lOut:
#                         continue
#                     val = pix[k, l]
#                     somme = somme + val
#                     count += 1
#             rpix[i, j] = somme/count
#     return result
#
#
# def dilate(im, radius):
#     pix = im.load()
#     result = Image.new("L", im.size)
#     rpix = result.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             maxV = 0
#             for k in range(i - radius, i + radius+1):
#                 for l in range(j - radius, j + radius+1):
#                     kOut = (k < 0) or (k > im.size[0] - 1)
#                     lOut = (l < 0) or (l > im.size[1] - 1)
#                     if kOut or lOut:
#                         continue
#                     val = pix[k, l]
#                     if(maxV < val):
#                         maxV = val
#             rpix[i, j] = maxV
#     return result
#
#
# def erode(im, radius):
#     pix = im.load()
#     result = Image.new("L", im.size)
#     rpix = result.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             minV = 255
#             for k in range(i - radius, i + radius+1):
#                 for l in range(j - radius, j + radius+1):
#                     kOut = (k < 0) or (k > im.size[0] - 1)
#                     lOut = (l < 0) or (l > im.size[1] - 1)
#                     if kOut or lOut:
#                         continue
#                     val = pix[k, l]
#                     if(minV > val):
#                         minV = val
#             rpix[i, j] = minV
#     return result
#
#
# def median(im, radius):
#     pix = im.load()
#     result = Image.new("L", im.size)
#     rpix = result.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = []
#             for k in range(i - radius, i + radius+1):
#                 for l in range(j - radius, j + radius+1):
#                     kOut = (k < 0) or (k > im.size[0] - 1)
#                     lOut = (l < 0) or (l > im.size[1] - 1)
#                     if kOut or lOut:
#                         continue
#                     val.append(pix[k, l])
#                 val.sort()
#             rpix[i, j] = val[len(val)//2]
#     return result
#
#
# def maxFilter(im, radius):
#     pix = im.load()
#     result = Image.new("L", im.size)
#     rpix = result.load()
#     for i in range(0, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = []
#             for k in range(i - radius, i + radius+1):
#                 for l in range(j - radius, j + radius+1):
#                     kOut = (k < 0) or (k > im.size[0] - 1)
#                     lOut = (l < 0) or (l > im.size[1] - 1)
#                     if kOut or lOut:
#                         continue
#                     if(k == i) and (l == j):
#                         continue
#                     val.append(pix[k, l])
#                 val.sort()
#             if pix[i, j] > val[-1]:
#                 rpix[i, j] = val[-1]
#             else:
#                 rpix[i, j] = pix[i, j]
#     return result
#
#
# def minFilter(im, radius):
#     pix = im.load()
#     result = Image.new("L", im.size)
#     rpix = result.load()
#     for i in range(1, im.size[0]):
#         for j in range(0, im.size[1]):
#             val = []
#             for k in range(i - radius, i + radius+1):
#                 for l in range(j - radius, j + radius+1):
#                     kOut = (k < 0) or (k > im.size[0] - 1)
#                     lOut = (l < 0) or (l > im.size[1] - 1)
#                     if kOut or lOut:
#                         continue
#                     if(k == i) and (l == j):
#                         continue
#                     val.append(pix[k, l])
#                 val.sort()
#             if pix[i, j] < val[0]:
#                 rpix[i, j] = val[0]
#             else:
#                 rpix[i, j] = pix[i, j]
#     return result
#
#
# def add(a, b):
#     newA, newB = normalize([a, b])
#     pixA = newA.load()
#     pixB = newB.load()
#     newImage = Image.new("RGB", a.size)
#     pix = newImage.load()
#     for i in range(0, newImage.size[0]):
#         for j in range(0, newImage.size[1]):
#             valA = pixA[i, j]
#             valB = pixB[i, j]
#             pix[i, j] = (valA[0] + valB[0],
#                          valA[1] + valB[1],
#                          valA[2] + valB[2])
#     return newImage
#
#
# def product(a, b):
#     newA, newB = normalize([a, b])
#     pixA = newA.load()
#     pixB = newB.load()
#     type(pixA)
#     newImage = Image.new("RGB", a.size)
#     pix = newImage.load()
#     for i in range(0, newImage.size[0]):
#         for j in range(0, newImage.size[1]):
#             valA = pixA[i, j]
#             valB = pixB[i, j]
#             pix[i, j] = ((valA[0] * valB[0])/255,
#                          (valA[1] * valB[1])/255,
#                          (valA[2] * valB[2])/255)
#     return newImage
#
#
# def copy(a, b, m):
#     newA, newB, newM = normalize([a, b, m])
#     pixA = newA.load()
#     pixB = newB.load()
#     pixM = newM.load()
#     newImage = Image.new("RGB", a.size)
#     pix = newImage.load()
#     for i in range(0, newImage.size[0]):
#         for j in range(0, newImage.size[1]):
#             if pixM[i, j] == (0, 0, 0):
#                 pix[i, j] = pixB[i, j]
#             else:
#                 pix[i, j] = pixA[i, j]
#     return newImage
#
#
# def max(images):
#     imgs = normalize(images)
#     newImage = Image.new("RGB", imgs[0].size)
#     pix = newImage.load()
#     for x in range(0, newImage.size[0]):
#         for y in range(0, newImage.size[1]):
#             valR = []
#             valG = []
#             valB = []
#             for i in imgs:
#                 newPix = i.load()
#                 valR.append(newPix[x, y][0])
#                 valG.append(newPix[x, y][1])
#                 valB.append(newPix[x, y][2])
#             valR.sort()
#             valG.sort()
#             valB.sort()
#             pix[x, y] = (valR[-1], valG[-1], valB[-1])
#     return newImage
#
#
# def min(images):
#     imgs = normalize(images)
#     newImage = Image.new("RGB", imgs[0].size)
#     pix = newImage.load()
#     for x in range(0, newImage.size[0]):
#         for y in range(0, newImage.size[1]):
#             valR = []
#             valG = []
#             valB = []
#             for i in imgs:
#                 newPix = i.load()
#                 valR.append(newPix[x, y][0])
#                 valG.append(newPix[x, y][1])
#                 valB.append(newPix[x, y][2])
#             valR.sort()
#             valG.sort()
#             valB.sort()
#             pix[x, y] = (valR[0], valG[0], valB[0])
#     return newImage
#
#
# def mediane(images):
#     imgs = normalize(images)
#     newImage = Image.new("RGB", imgs[0].size)
#     pix = newImage.load()
#     for x in range(0, newImage.size[0]):
#         for y in range(0, newImage.size[1]):
#             valR = []
#             valG = []
#             valB = []
#             for i in imgs:
#                 newPix = i.load()
#                 valR.append(newPix[x, y][0])
#                 valG.append(newPix[x, y][1])
#                 valB.append(newPix[x, y][2])
#             valR.sort()
#             valG.sort()
#             valB.sort()
#             pix[x, y] = (valR[len(valR)/2],
#                          valG[len(valG)/2],
#                          valB[len(valB)/2])
#     return newImage
#
#
# def avg(images):
#     imgs = normalize(images)
#     newImage = Image.new("RGB", imgs[0].size)
#     pix = newImage.load()
#     for x in range(0, newImage.size[0]):
#         for y in range(0, newImage.size[1]):
#             valR = []
#             valG = []
#             valB = []
#             for i in imgs:
#                 newPix = i.load()
#                 valR.append(newPix[x, y][0])
#                 valG.append(newPix[x, y][1])
#                 valB.append(newPix[x, y][2])
#             r = 0
#             g = 0
#             b = 0
#             for j in range(0, len(valR)-1):
#                 r += valR[j]
#                 g += valG[j]
#                 b += valB[j]
#             pix[x, y] = (r/len(valR), g/len(valG), b/len(valB))
#     return newImage
#
#
# def comparaisonHistoFactor(histoA, histoB, factor):
#     # print histoA
#     hA = normHisto(histoA)
#     hB = normHisto(histoB)
#     distance = 0.
#     for i in range(0, 255):
#         distance += ((fabs(hA[i] - hB[i]))**factor)/len(hA)
#     return distance
#
#
# def comparaisonHisto3channels2(histoA, histoB, factor):
#     result = []
#     finale = 0.
#     for c in range(3):
#         result.append(comparaisonHistoFactor(histoA[c], histoB[c], factor))
#     for i in range(0, 3):
#         finale += result[i]
#     return round((finale * 100.), 2)
