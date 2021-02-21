from datetime import date, datetime
from google.cloud import firestore

database_name = "is-my-town-safe"

'''
Takes a document_name in a firestore db, a key that corresponds to a value in a firestore db
Returns the value of the key, or None if neither the document or the key can be found
'''
def read_from_db(document_name, key):
    db = firestore.Client()
    doc = db.collection(database_name).document(str(document_name)).get()
    if doc.exists:
        doc_dict = doc.to_dict()
        return doc_dict.get(key)
    else:
        return None

'''
Takes a document_name in a firestore db
Returns a dict of the document or None if the document cannot be found
'''
def read_from_db(document_name):
    db = firestore.Client()
    doc = db.collection(database_name).document(str(document_name)).get()
    if doc.exists:
        doc_dict = doc.to_dict()
        return doc_dict
    else:
        return None

'''
Returns the number of days since 1970-01-01, using the current time and local timezone
'''
def days_since_epoch():
    return int(int(datetime.now().timestamp()) / 60 / 60 / 24)    # may be a better way to calculate this



def main():




main()