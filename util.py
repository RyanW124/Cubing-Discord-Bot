import nextcord
testID = 876792128154525727
emojis = {'red': '🟥', 'yellow': "🟨", 'white': "⬜", 'green': '🟩', 'blue': '🟦', 'orange': '🟧'}
colors = ['white', 'orange', 'green', 'red', 'blue', 'yellow']

def list_to_str(L):
    ret = ''
    for i in L:
        ret += str(i)
    return ret

def list_to_emoji(L):
    ret = ''
    for i in L:
        ret += emojis[colors[i]]
    return ret

async def close_view(msg):
    await msg.edit(view=None)

def get_col(matrix, i):
    return [row[i] for row in matrix]
def wrap(l):
    return [[i] for i in l]
def matrix_multiply(m1, m2):
    ret = [[0]*len(m2[0]) for _ in range(len(m1))]
    for i in range(len(m1)):
        for j in range(len(m2[0])):
            for x1, x2 in zip(m1[i], get_col(m2, j)):
                ret[i][j] += x1 * x2
    return ret

def make_error(msg):
    embed = nextcord.Embed(colour=nextcord.Color.red())
    embed.set_author(name="Error")
    embed.description = msg
    return embed