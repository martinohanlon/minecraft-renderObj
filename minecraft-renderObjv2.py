#www.stuffaboutcode.com
#Raspberry Pi, Minecraft - Create 3D Model from Obj file
# Version 2 - draws complete faces rather than wireframes and uses materials

#import the minecraft.py module from the minecraft directory
import minecraft.minecraft as minecraft
#import minecraft block module
import minecraft.block as block
#import time, so delays can be used
import time
#import datetime, to get the time!
import datetime

# class to create 3d filled polygons
class MinecraftDrawing:
    def __init__(self, mc):
        self.mc = mc

    # draw point
    def drawPoint3d(self, x, y, z, blockType, blockData=None):
        self.mc.setBlock(x,y,z,blockType,blockData)
        #print "x = " + str(x) + ", y = " + str(y) + ", z = " + str(z)

    # draws a face, when passed a collection of vertices which make up a polyhedron
    def drawFace(self, vertices, blockType, blockData=None):
        
        # get the edges of the face
        edgesVertices = []
        # persist first vertex
        firstVertex = vertices[0]
        # loop through vertices and get edges
        vertexCount = 0
        for vertex in vertices:
            vertexCount+=1
            if vertexCount > 1:
                # got 2 vertices, get the points for the edge
                edgesVertices = edgesVertices + self.getLine(lastVertex.x, lastVertex.y, lastVertex.z, vertex.x, vertex.y, vertex.z)
                #print "x = " + str(lastVertex.x) + ", y = " + str(lastVertex.y) + ", z = " + str(lastVertex.z) + " x2 = " + str(vertex.x) + ", y2 = " + str(vertex.y) + ", z2 = " + str(vertex.z)
            # persist the last vertex found    
            lastVertex = vertex
        # get edge between the last and first vertices
        edgesVertices = edgesVertices + self.getLine(lastVertex.x, lastVertex.y, lastVertex.z, firstVertex.x, firstVertex.y, firstVertex.z)

        # sort edges vertices
        def keyX( point ): return point.x
        def keyY( point ): return point.y
        def keyZ( point ): return point.z
        edgesVertices.sort( key=keyZ )
        edgesVertices.sort( key=keyY )
        edgesVertices.sort( key=keyX )

        # not very performant but wont have gaps between in complex models
        for vertex in edgesVertices:
            vertexCount+=1
            # got 2 vertices, draw lines between them
            if (vertexCount > 1):
                self.drawLine(lastVertex.x, lastVertex.y, lastVertex.z, vertex.x, vertex.y, vertex.z, blockType, blockData)
                #print "x = " + str(lastVertex.x) + ", y = " + str(lastVertex.y) + ", z = " + str(lastVertex.z) + " x2 = " + str(vertex.x) + ", y2 = " + str(vertex.y) + ", z2 = " + str(vertex.z)
            # persist the last vertex found
            lastVertex = vertex
        
    # draw's all the points in a collection of vertices with a block
    def drawVertices(self, vertices, blockType, blockData=None):
        for vertex in vertices:
            self.drawPoint3d(vertex.x, vertex.y, vertex.z, blockType, blockData)

    # draw line
    def drawLine(self, x1, y1, z1, x2, y2, z2, blockType, blockData):
        self.drawVertices(self.getLine(x1, y1, z1, x2, y2, z2), blockType, blockData)
    
    # returns points on a line
    def getLine(self, x1, y1, z1, x2, y2, z2):

        # return maximum of 2 values
        def MAX(a,b):
            if a > b: return a
            else: return b

        # return step
        def ZSGN(a):
            if a < 0: return -1
            elif a > 0: return 1
            elif a == 0: return 0

        # list for vertices
        vertices = []

        # if the 2 points are the same, return single vertice
        if (x1 == x2 and y1 == y2 and z1 == z2):
            vertices.append(minecraft.Vec3(x1, y1, z1))
                            
        # else get all points in edge
        else:
        
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1

            ax = abs(dx) << 1
            ay = abs(dy) << 1
            az = abs(dz) << 1

            sx = ZSGN(dx)
            sy = ZSGN(dy)
            sz = ZSGN(dz)

            x = x1
            y = y1
            z = z1

            # x dominant
            if (ax >= MAX(ay, az)):
                yd = ay - (ax >> 1)
                zd = az - (ax >> 1)
                loop = True
                while(loop):
                    vertices.append(minecraft.Vec3(x, y, z))
                    if (x == x2):
                        loop = False
                    if (yd >= 0):
                        y += sy
                        yd -= ax
                    if (zd >= 0):
                        z += sz
                        zd -= ax
                    x += sx
                    yd += ay
                    zd += az
            # y dominant
            elif (ay >= MAX(ax, az)):
                xd = ax - (ay >> 1)
                zd = az - (ay >> 1)
                loop = True
                while(loop):
                    vertices.append(minecraft.Vec3(x, y, z))
                    if (y == y2):
                        loop=False
                    if (xd >= 0):
                        x += sx
                        xd -= ay
                    if (zd >= 0):
                        z += sz
                        zd -= ay
                    y += sy
                    xd += ax
                    zd += az
            # z dominant
            elif(az >= MAX(ax, ay)):
                xd = ax - (az >> 1)
                yd = ay - (az >> 1)
                loop = True
                while(loop):
                    vertices.append(minecraft.Vec3(x, y, z))
                    if (z == z2):
                        loop=False
                    if (xd >= 0):
                        x += sx
                        xd -= az
                    if (yd >= 0):
                        y += sy
                        yd -= az
                    z += sz
                    xd += ax
                    yd += ay
                    
        return vertices

def load_obj(filename, defaultBlock, materials) :
    V = [] #vertex
    T = [] #texcoords
    N = [] #normals
    F = [] #face indexies
    MF = [] #materials to faces

    currentMaterial = defaultBlock

    fh = open(filename)
    for line in fh :
        if line[0] == '#' : continue
        line = line.strip().split(' ')
        if line[0] == 'v' : #vertex
            V.append(line[1:])
        elif line[0] == 'vt' : #tex-coord
            T.append(line[1:])
        elif line[0] == 'vn' : #normal vector
            N.append(line[1:])
        elif line[0] == 'f' : #face
            face = line[1:]
            for i in range(0, len(face)) :
                face[i] = face[i].split('/')
                # OBJ indexies are 1 based not 0 based hence the -1
                # convert indexies to integer
                for j in range(0, len(face[i])) :
                    if face[i][j] != "":
                        face[i][j] = int(face[i][j]) - 1
            #append the material currently in use to the face
            F.append(face)
            MF.append(currentMaterial)
    
        elif line[0] == 'usemtl': # material
            
            usemtl = line[1]
            if (usemtl in materials.keys()):
                currentMaterial = materials[usemtl]
            else:
                currentMaterial = defaultBlock
                print "Warning: Couldn't find '" + str(usemtl) + "' in materials using default"

    return V, T, N, F, MF

# strips the x,y,z co-ords from a vertex line, scales appropriately, rounds and converts to int
def getVertexXYZ(vertexLine, scale, startCoord, swapYZ):
    # convert, round and scale
    x = int((float(vertexLine[0]) * scale) + 0.5)
    y = int((float(vertexLine[1]) * scale) + 0.5)
    z = int((float(vertexLine[2]) * scale) + 0.5)
    # add startCoord to x,y,z
    x = x + startCoord.x
    y = y + startCoord.y
    z = z + startCoord.z
    # swap y and z coord if needed
    if swapYZ == True:
        swap = y
        y = z
        z = swap
    return x, y, z

# main program
if __name__ == "__main__":

    print datetime.datetime.now()

    #Connect to minecraft by creating the minecraft object
    # - minecraft needs to be running and in a game
    mc = minecraft.Minecraft.create()

    #Create minecraft drawing class
    mcDrawing = MinecraftDrawing(mc)
    
    #Load objfile and set constants

    # COORDSSCALE = factor to scale the co-ords by
    # STARTCOORD = where to start the model, the relative position 0
    # CLEARAREA1/2 = 2 points the program should clear an area in between to put the model in
    # SWAPYZ = True to sway the Y and Z dimension
    # MATERIALS = a dictionary object which maps materials in the obj file to blocks in minecraft
    # DEFAULTBLOCK = the default type of block to build the model in, used if a material cant be found

    # Cube
    #COORDSSCALE = 10
    #STARTCOORD = minecraft.Vec3(0,10,0)
    #CLEARAREA1 = minecraft.Vec3(-10, 0, -10)
    #CLEARAREA2 = minecraft.Vec3(10, 20, 10)
    #DEFAULTBLOCK = [block.STONE, None]
    #MATERIALS = {}
    #SWAPYZ = False
    #vertices,textures,normals,faces,materials = load_obj("cube.obj", DEFAULTBLOCK, MATERIALS)

    # Shuttle
    #COORDSSCALE = 6
    #STARTCOORD = minecraft.Vec3(-60,0,20)
    #CLEARAREA1 = minecraft.Vec3(-30, 5, -30)
    #CLEARAREA2 = minecraft.Vec3(-90, 50, 30)
    #DEFAULTBLOCK = [block.WOOL.id,0]
    #MATERIALS = {"glass": [block.GLASS.id, None],
    #             "bone": [block.WOOL.id, 0],
    #             "fldkdkgrey": [block.WOOL.id, 7],
    #             "redbrick": [block.WOOL.id, 14],
    #             "black": [block.WOOL.id, 15],
    #             "brass": [block.WOOL.id, 1],
    #             "dkdkgrey": [block.WOOL.id, 7]}
    #SWAPYZ = True
    #vertices,textures,normals,faces,materials = load_obj("shuttle.obj", DEFAULTBLOCK, MATERIALS)

    # Shyscraper
    #COORDSSCALE = 1.4
    #STARTCOORD = minecraft.Vec3(0,10,15)
    #CLEARAREA1 = minecraft.Vec3(-30, -3, -15)
    #CLEARAREA2 = minecraft.Vec3(30, 65, 35)
    #DEFAULTBLOCK = [block.IRON_BLOCK, None]
    #MATERIALS = {}
    #SWAPYZ = False
    #vertices,textures,normals,faces,materials = load_obj("skyscraper.obj", DEFAULTBLOCK, MATERIALS)

    # Head
    #COORDSSCALE = 3
    #STARTCOORD = minecraft.Vec3(0,-431,-60)
    #CLEARAREA1 = minecraft.Vec3(-30, -30, -30)
    #CLEARAREA2 = minecraft.Vec3(30, 65, -110)
    #DEFAULTBLOCK = [block.GOLD_BLOCK, None]
    #MATERIALS = {}
    #SWAPYZ = False
    #vertices,textures,normals,faces,materials = load_obj("head.obj", DEFAULTBLOCK, MATERIALS)

    # Cessna
    #COORDSSCALE = 2
    #STARTCOORD = minecraft.Vec3(-75, 25, -60)
    #CLEARAREA1 = minecraft.Vec3(-30, 15, -30)
    #CLEARAREA2 = minecraft.Vec3(-100, 65, -90)
    #DEFAULTBLOCK = [block.WOOD_PLANKS, None]
    #MATERIALS = {}
    #SWAPYZ = False
    #vertices,textures,normals,faces,materials = load_obj("cessna.obj", DEFAULTBLOCK, MATERIALS)

    # New York
    #COORDSSCALE = 0.1
    #STARTCOORD = minecraft.Vec3(-185, 0, 140)
    #CLEARAREA1 = minecraft.Vec3(-130, 0, -130)
    #CLEARAREA2 = minecraft.Vec3(130, 65, 130)
    #DEFAULTBLOCK = [block.IRON_BLOCK, None]
    #MATERIALS = {"Default_Material": [block.WOOL.id, 0],
    #             "Color_A01": [block.WOOL.id, 14],
    #             "0131_Silver": [block.IRON_BLOCK, None],
    #             "0075_ForestGreen": [block.WOOL.id, 13],
    #             "0137_Black": [block.WOOL.id, 15],
    #             "Black": [block.WOOL.id, 15],
    #             "Medium_Brown": [block.WOOL.id, 12],
    #             "0056_Yellow": [block.WOOL.id, 4],
    #             "0020_Red": [block.WOOL.id, 14],
    #             "0102_RoyalBlue": [block.WOOL.id, 11],
    #             "Color_E01": [block.WOOL.id, 4],
    #             "Color_E02": [block.WOOL.id, 4],
    #             "Color_B01": [block.WOOL.id, 1],
    #             "Charcoal": [block.WOOL.id, 7],
    #             "Material2": [block.WOOL.id, 0],
    #             "Beige2": [block.SANDSTONE, None],
    #             "DarkGoldenrod": [block.GOLD_BLOCK, None],
    #             "Beige1": [block.SANDSTONE, None],
    #             "jean_blue": [block.WOOL.id, 3],
    #             "Gold1": [block.GOLD_BLOCK, None],
    #             "WhiteSmoke": [block.WOOL.id, 8],
    #             "0118_Thistle": [block.WOOL.id, 6],
    #             "Color_D23": [block.WOOL.id, 7],
    #             "Color_B23": [block.WOOL.id, 12],
    #             "Color_009": [block.WOOL.id, 15],
    #             "Color_D01": [block.WOOL.id, 1],
    #             "Color_A06": [block.WOOL.id, 14],
    #             "Color_D03": [block.WOOL.id, 4],
    #             "0063_GreenYellow": [block.WOOL.id, 5]}
    #SWAPYZ = False
    #vertices,textures,normals,faces,materials = load_obj("NY_LIL.obj", DEFAULTBLOCK, MATERIALS)

    # Nottingham Forest City Ground
    #COORDSSCALE = 0.35
    #STARTCOORD = minecraft.Vec3(0, -1, 0)
    #CLEARAREA1 = minecraft.Vec3(-50, -1, -50)
    #CLEARAREA2 = minecraft.Vec3(50, 20, 50)
    #DEFAULTBLOCK = [block.DIRT,None]
    #MATERIALS = {"Default_Material": [block.STONE.id,None],
    #             "Black": [block.WOOL.id,15],
    #             "Asphalt_Old": [block.WOOL.id,7],
    #             "GhostWhite": [block.WOOL.id,0],
    #             "Brick_Flemish_Bond": [block.BRICK_BLOCK,None],
    #             "Concrete_Brushed": [block.STONE,None],
    #             "Metal_Brushed": [block.IRON_BLOCK,None],
    #             "Roofing_Metal_Standing_Seam_Blue": [block.WOOL.id,8],
    #             "White": [block.WOOL.id,0],
    #             "Metal_Brushed1": [block.IRON_BLOCK,None],
    #             "Rouge3141": [block.WOOL.id,14],
    #             "roof": [block.WOOL.id,8],
    #             "Metal_Aluminum_Anodized": [block.IRON_BLOCK,None],
    #             "Translucent_Glass_Safety": [block.GLASS, None],
    #             "Translucent_Glass_Safety1": [block.GLASS, None],
    #             "Safety_Glass2": [block.GLASS, None],
    #             "Red": [block.WOOL.id,14],
    #             "goal_net1": [block.WOOL.id,0],
    #             "Black": [block.WOOL.id,15]}
    #SWAPYZ = False
    #vertices,textures,normals,faces, materials = load_obj("City_Ground-Notts.obj", DEFAULTBLOCK, MATERIALS)

    # Raspbery Pi
    COORDSSCALE = 1350
    STARTCOORD = minecraft.Vec3(-50, 0, 0)
    CLEARAREA1 = minecraft.Vec3(-100, 0, -100)
    CLEARAREA2 = minecraft.Vec3(100, 20, 10)
    DEFAULTBLOCK = [block.DIRT,None]
    MATERIALS = {"Default_Material": [block.WOOL.id, 0],
                 "Material1": [block.WOOL.id, 5],
                 "Goldenrod": [block.WOOL.id, 1],
                 "0136_Charcoal": [block.WOOL.id, 7],
                 "Gray61": [block.WOOL.id, 7],
                 "Charcoal": [block.WOOL.id, 7],
                 "Color_002": [block.WOOL.id, 8],
                 "Color_008": [block.WOOL.id, 4],
                 "Plastic_Green": [block.WOOL.id, 5],
                 "MB_Pastic_White": [block.WOOL.id, 0],
                 "IO_Shiny": [block.IRON_BLOCK, None],
                 "Material4": [block.GRASS, None],
                 "Gainsboro3": [block.WOOL.id, 5],
                 "CorrogateShiny1": [block.IRON_BLOCK, None],
                 "Gold": [block.GOLD_BLOCK, None],
                 "0129_WhiteSmoke": [block.WOOL.id, 0],
                 "Color_005": [block.WOOL.id, 0],
                 "USB_IO": [block.WOOL.id, 11],
                 "_Metal": [block.IRON_BLOCK, None],
                 "0132_LightGray": [block.WOOL.id, 8]}
    SWAPYZ = False
    vertices,textures,normals,faces, materials = load_obj("RaspberryPi.obj", DEFAULTBLOCK, MATERIALS)

    print "obj file loaded"

    #Post a message to the minecraft chat window 
    mc.postToChat("Hi, Minecraft 3d model maker, www.stuffaboutcode.com")
    
    # clear a suitably large area
    mc.setBlocks(CLEARAREA1.x, CLEARAREA1.y, CLEARAREA1.z, CLEARAREA2.x, CLEARAREA2.y, CLEARAREA2.z, block.AIR)
    time.sleep(10)

    faceCount = 0
    # loop through faces
    for face in faces:
        faceVertices = []
        
        # loop through vertex's in face and call drawFace function
        for vertex in face:
            #strip co-ords from vertex line
            vertexX, vertexY, vertexZ = getVertexXYZ(vertices[vertex[0]], COORDSSCALE, STARTCOORD, SWAPYZ)

            faceVertices.append(minecraft.Vec3(vertexX,vertexY,vertexZ))
                   
        # draw the face
        mcDrawing.drawFace(faceVertices, materials[faceCount][0], materials[faceCount][1])
        faceCount = faceCount + 1

    mc.postToChat("Model complete, www.stuffaboutcode.com")

    print datetime.datetime.now()
