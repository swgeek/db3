# older versions of stuff, not used but some useful code in here if needed

# may have to do this to extract unicode values
#	asciiString = stringToHash.encode('ascii', 'ignore')
def HashString(stringToHash):
	asciiString = stringToHash
	# uncomment this if have problems with the hash because of unicode
	#asciiString = stringToHash.encode('utf-8')

	hash = hashlib.sha1(asciiString)
	hashDigest = hash.hexdigest()
	return hashDigest.upper()

