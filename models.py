from app import db


number_identifier = db.Table('number_identifier',
                             db.Column('number_index', db.Integer, db.ForeignKey('numbers.index')),
                             db.Column('wcode_index', db.Integer, db.ForeignKey('wcodes.index'))
                             )


class Number(db.Model):
    __tablename__ = 'numbers'

    index = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, unique=True)

    def __init__(self, number):
        self.value = number

    def __repr__(self):
        return '<{}>'.format(self.value)

    def serialize(self):
        return {'value': self.value}


class Wcode(db.Model):
    __tablename__ = 'wcodes'

    index = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, unique=True)
    year = db.Column(db.Integer)
    numbers = db.relationship(Number, secondary=number_identifier, backref='wcodes')
    bonus_index = db.Column(db.Integer, db.ForeignKey('numbers.index'))
    bonus = db.relationship(Number, backref='bwcodes')

    def __init__(self, no, year, n1, n2, n3, n4, n5, n6, bonus):
        self.no = no
        self.year = year
        self.numbers.append(n1)
        self.numbers.append(n2)
        self.numbers.append(n3)
        self.numbers.append(n4)
        self.numbers.append(n5)
        self.numbers.append(n6)
        self.bonus = bonus

    def __repr__(self):
        return '<number: {}, bonus: {}>'.format(self.numbers, self.bonus)

    def serialize(self):
        return {
            'no': self.no,
            'year': self.year,
            'numbers': self.numbers,
            'bonus': self.bonus,
        }


class Lowcode(db.Model):
    __tablename__ = 'lowcodes'

    index = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, unique=True)
    year = db.Column(db.Integer)
    one = db.Column(db.Integer)
    two = db.Column(db.Integer)
    three = db.Column(db.Integer)
    four = db.Column(db.Integer)
    five = db.Column(db.Integer)
    six = db.Column(db.Integer)
    bonus = db.Column(db.Integer)
