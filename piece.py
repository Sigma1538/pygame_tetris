class Tetris:
    def __init__(self, figure,color,number):
        self.figure = figure
        self.pose = 0
        self.color = color
        self.number = number #1~7
        self.grid_x,self.grid_y = (4,-1)
        self.real_figure = figure

    def rotate(self, pose):
        transform = None

        if pose == 0:
            transform = self.figure
        elif pose == 1:
            transform = [[0 for i in range(len(self.figure))] for j in range(len(self.figure[0]))]
            for i in range(0, len(self.figure)):
                for j in range(0, len(self.figure[i])):
                    transform[len(self.figure[i]) - j - 1][i] = self.figure[i][j]
        elif pose == 2:
            transform = [[0 for i in range(len(self.figure[0]))] for j in range(len(self.figure))]
            for i in range(0, len(self.figure)):
                for j in range(0, len(self.figure[i])):
                    transform[len(self.figure) - i - 1][len(self.figure[i]) - j - 1] = self.figure[i][j]
        elif pose == 3:
            transform = [[0 for i in range(len(self.figure))] for j in range(len(self.figure[0]))]
            for i in range(0, len(self.figure)):
                for j in range(0, len(self.figure[i])):
                    transform[j][len(self.figure) - i - 1] = self.figure[i][j]
        else:
            transform = self.figure

        self.real_figure = transform  
        return transform
