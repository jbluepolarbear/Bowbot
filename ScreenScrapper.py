import Image
import ImageChops
import ImageGrab
import ImageDraw

import Queue

#class for holding information of shooting targets
class Entity(object):
    def __init__(self, group):
        self.make_entity_from_group(group)
        self.area = self.width*self.height

    #find the dimensions of the provided grouping and creates an entity.
    def make_entity_from_group(self, group):
        x1 = x2 = group[0][0]
        y1 = y2 = group[0][1]

        for x in group:
            if x[0] > x2:
                x2 = x[0]
            if x[0] < x1:
                x1 = x[0]
            if x[1] > y2:
                y2 = x[1]
            if x[1] < y1:
                y1 = x[1]

        self.width = x2 - x1
        self.height = y2 - y1
        self.center = ((x2+x1)/2.0,(y2+y1)/2.0)

#class to grab the screen compare it to a base, compare them and then group the differences.
class ScreenScraper(object):
    def __init__(self, createFile = False):
        self.createFile = createFile

    def grab_screen(self, savename = 'output,png'):
        image = ImageGrab.grab((75, 230, 945, 515))

        self.save_image(savename, image)

        return image

    def save_image(self, filename, image):
        if self.createFile:
            with open(filename, "wb") as outfile:
                image.save(outfile)

    #create base image for future compare.
    def CreateBase(self):
        self.baseImage = self.grab_screen('base.png')

    #finds the differences between the new image and the base.
    def CreateContrast(self):
        image = self.grab_screen('comparer.png')

        diffImage = ImageChops.difference(self.baseImage, image)

        self.save_image('diff.png', diffImage)

        imageWidth, imageHeight = diffImage.size

        outlist = [(0,0,0) for x in xrange(imageWidth*imageHeight)]

        imgdata = list(diffImage.getdata())
        for x in xrange(imageWidth):
            for y in xrange(imageHeight):
                color = imgdata[y*imageWidth+x]
        ##        if color != (0,0,0):
        ##            outlist[y*imageWidth+x] = (255,0,0)
                if color[0] > 20 or color[1] > 20 or color[2] > 20:
                    outlist[y*imageWidth+x] = (255,0,0)
        ##            print color

        self.changedImage = Image.new('RGB', (imageWidth, imageHeight))
        self.changedImage.putdata(outlist)

        self.save_image('changed.png', self.changedImage)

    #create entities from groupings of the contrast compare.
    def CreateEntities(self):
        image = self.changedImage.copy()

        imageWidth, imageHeight = image.size

        imgdata = list(image.getdata())

        visited = [False for x in xrange(imageWidth*imageHeight)]

        def findgroup( x, y ):
            q = Queue.Queue()
            group = []
            if imgdata[y*imageWidth+x] == (0,0,0) or visited[y*imageWidth+x]:
                return group

            q.put((x,y))
            while not q.empty():
                n = q.get()
                if imgdata[n[1]*imageWidth+n[0]] == (255,0,0):
                    group.append(n)
                    visited[n[1]*imageWidth+n[0]] = True
                areas = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
                for x in areas:
                    nn = (n[0]+x[0], n[1]+x[1])
                    if 0 < nn[0] < imageWidth and 0 < nn[1] < imageHeight:
                        if imgdata[nn[1]*imageWidth+nn[0]] == (255,0,0) and not visited[nn[1]*imageWidth+nn[0]]:
                            q.put(nn)
                            visited[nn[1]*imageWidth+nn[0]] = True
            return group

        groups = []
        for x in xrange(imageWidth):
            for y in xrange(imageHeight):
                if imgdata[y*imageWidth+x] == (0,0,0) or visited[y*imageWidth+x]:
                    continue
                #print imgdata[y*imageWidth+x]
                groups.append(findgroup(x, y))

        #print 'found: '+str(len(groups))

        entities = []
        for x in groups:
            e = Entity(x)
            #print 'width: '+str(e.width)+', '+'height: '+str(e.height)
            #print 'x: '+str(e.center[0])+', y: '+str(e.center[1])
            if e.area > 100 and e.center[0]>200 and len(x)/100 > 0.4:
                entities.append(e)

        #print 'number of entities: '+str(len(entities))

        draw = ImageDraw.Draw(image)
        for x in entities:
            draw.line((x.center[0]-x.width/2, x.center[1]-x.height/2)+(x.center[0]+x.width/2, x.center[1]-x.height/2),fill='rgb(0,255,0)')
            draw.line((x.center[0]+x.width/2, x.center[1]-x.height/2)+(x.center[0]+x.width/2, x.center[1]+x.height/2),fill='rgb(0,255,0)')
            draw.line((x.center[0]+x.width/2, x.center[1]+x.height/2)+(x.center[0]-x.width/2, x.center[1]+x.height/2),fill='rgb(0,255,0)')
            draw.line((x.center[0]-x.width/2, x.center[1]+x.height/2)+(x.center[0]-x.width/2, x.center[1]-x.height/2),fill='rgb(0,255,0)')

        del draw

        self.save_image('boxed.png', image)

        return entities

if __name__ == '__main__':
    import time

    ss = ScreenScraper(True)
    time.sleep(5)
    ss.CreateBase()
    time.sleep(5)
    ss.CreateContrast()
    entities = ss.CreateEntities()

