from app.models import Block

def get_block():
    blocks = Block.query.all()
    return blocks

