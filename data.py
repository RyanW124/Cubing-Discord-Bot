import nextcord
class User:
    users = {}
    def __init__(self, id):
        self.id = id
        # self.times = [Time(random.uniform(10, 20), "3x3", "", False) for _ in range(12)] + [Time(10, "3x3", "", False, 2), Time(12, "3x3", "", False, 2)]
        self.virtual = None
        self.times = []
        self.current = None
        self.rotation = (-10, 10, 0)
        self.msg = None
        self.match = None
        self.virtualing = False
        self.timing = False
    async def change_msg(self, msg):
        if self.msg is not None:
            await self.msg.edit(view=None)
        self.msg = msg

    @classmethod
    def get_user(cls, id):
        if id not in cls.users:
            cls.users[id] = User(id)
        return cls.users[id]


class Time:
    def __init__(self, time, stype, scramble, stime=True, penalty=0, *, special=None):
        self.time = time
        self.stype = stype
        self.scramble = scramble
        self.stime = stime
        self.special = special
        if special == "DNF":
            penalty = 2
        self.penalty = penalty
    @classmethod
    def get_embed(cls, user, fil, interaction, stats=False):
        embed = nextcord.Embed(colour=nextcord.Color.green())
        if fil == '0':
            embed.description = "No filter"
        elif fil == '1':
            embed.description = "Others only"
        else:
            embed.description = f"{fil}x{fil} only"
        embed.set_author(name=f"{interaction.user.name}'s {'stats' if stats else 'solves'}",
                         icon_url=interaction.user.display_avatar.url)
        times = user.times
        i = len(times) - 1
        count = 0
        ts = []
        while count < 12 and i >= 0:
            time = times[i]
            if fil == "0" or fil == '1' and time.stype == "Other" or time.stype == f"{fil}x{fil}":
                if not stats:
                    embed.add_field(name=f"Solve #{i + 1}: ", value=str(time), inline=False)
                ts.append(time)
                count += 1
            i -= 1
        if count == 0:
            embed.add_field(name=f"There are no solves", value='Do a solve to display here!')
        elif stats:
            stat_texts = [ts[0], cls.mo(ts)[0], cls.ao(ts)[0], cls.ao(ts, 12)[0],
                          min(ts, key=lambda i: float('inf') if i.isDNF else i),
                          cls.best_mo(ts)[0], cls.best_ao(ts)[0], cls.best_ao(ts, 12)[0]]
            texts = ["Time", "mo3", "ao5", "ao12", "Best Time", "Best mo3", "Best ao5", "Best ao12"]
            for name, value in zip(texts, stat_texts):
                embed.add_field(name=name + ": ", value=str(value), inline=False)

        return embed
    @classmethod
    def sum(cls, l):
        s = cls.num(0)
        for i in l:
            s += i
        return s
    @classmethod
    def mo(cls, t, n=3):
        if len(t) < n:
            return cls.NA, t
        for i in t[:n]:
            if i.isDNF:
                return cls.DNF, t[:n]
        return cls.sum(t[:n]) / n, t[:n]
    @classmethod
    def ao(cls, t, n=5):
        if len(t) < n:
            return Time.NA, t
        dnfCount = 0
        mini, maxi, s = Time.DNF, Time(0, '', ''), cls.num(0)
        for i in t[:n]:
            if i.isDNF:
                maxi = Time.DNF
                dnfCount += 1
                if dnfCount > 1:
                    return Time.DNF, t[:n]
            else:
                mini = min(mini, i)
                maxi = max(maxi, i)
                s += i.time
        # s = s.time
        return ((s - mini) / (n - 2), t[:n]) if maxi.isDNF else ((s - mini - maxi) / (n - 2), t[:n])

    @classmethod
    def best_mo(cls, t, n=3):
        ret = Time.NA
        l = t
        for i in range(len(t) - n + 1):
            new, newl = cls.mo(t[i:i + n], n)
            if new < ret:
                ret = new
                l = newl
        return ret, l

    @classmethod
    def best_ao(cls, t, n=5):
        ret = Time.NA
        l = t
        for i in range(len(t) - n + 1):
            new, newl = cls.ao(t[i:i + n], n)
            if new < ret:
                ret = new
                l = newl
        return ret, l

    @classmethod
    def num(cls, n):
        return cls(n, "Other", "", special="Num")
    @classmethod
    @property
    def NA(cls):
        return cls(0, "Other", "", special="N/A")
    @classmethod
    @property
    def DNF(cls):
        return cls(0, "Other", "", special="DNF")
    def endtime(self, time):
        if self.stime:
            self.time = time - self.time
    def ok(self):
        if self.penalty == 1:
            self.time -= 2
        self.penalty = 0
    def plustwo(self):
        if self.penalty == 1:
            return
        self.time += 2
        self.penalty = 1
    def dnf(self):
        if self.penalty == 1:
            self.time -= 2
        self.penalty = 2
    @property
    def isDNF(self):
        return self.penalty == 2
    def __truediv__(self, other):
        return Time.num(self.time/other)
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Time.num(self.time + other)
        return Time.DNF if self.isDNF or other.isDNF else Time.num(self.time + other.time)
    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Time.num(self.time - other)
        return Time.DNF if self.isDNF or other.isDNF else Time.num(self.time - other.time)
    def __gt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.time > other
        if other.special == "N/A":
            return True
        return self.isDNF or (not other.isDNF and self.time > other.time)
    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.time < other
        if other.special == "N/A":
            return True
        return other.isDNF or (not self.isDNF and self.time < other.time)
    @classmethod
    def str(cls, t):
        return str(cls.num(t) if isinstance(t, int) else t)
    def __repr__(self):
        if self.special == "DNF":
            return "DNF"
        elif self.special == "N/A":
            return "N/A"
        m, s = divmod(self.time, 60)
        h, m = divmod(m, 60)
        text = ''
        if h:
            text += str(int(h)) + 'h '
        if m:
            text += str(int(m)) + 'm '
        text += str(s)[:4] + 's'
        if self.penalty == 1:
            text+='+'
        elif self.penalty == 2:
            text = f"DNF({text})"
        return text