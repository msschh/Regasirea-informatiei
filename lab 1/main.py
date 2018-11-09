import retriveInfo as retr
import checkPhrase as checkPh

def main():
    indexDictionary, fileName, dictionaryAsAString = retr.retriveInfo()
    checkPh.checkPhrase('we are', indexDictionary, fileName, dictionaryAsAString)

main()
