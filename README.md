## Description
kobocollections is a python script to help organize books into a hierarchy for the Kobo e-reader. Using the Tier1/Tier2/Tier3 syntax for collections. 

The hierarchy you want for any book is put into the tag field for that book with #KB in front. The script will interpret the following string (until the EOL or a comma) to be the collection definition for that book. 

So - if you want a hierarchy that looks like

	Fiction
		Science Fiction
			Asimov
				Book
				Book
				Book
			
Then the tag definition would be #KB Fiction/Science Fiction/Asimov

If you want to have a clear series definition then the script looks at the series column and adds that to the hierarchy. So if you had the Foundation trilogy and you had them marked as Foundation [1] etc in the series field then the hierarchy would look like

	Fiction
		Science Fiction
			Asimov
				Foundation
					01 - Foundation
					02 - Foundation and Empire
					03 - Second Foundation
					
##Usage

The script requires two custom columns in calibre. By default these should be 'collections' and 'processed' but you can name them anything as long as you update the definition at the top of the script. 

The other thing is to put in the path name of the directory that holds the calibre library. Again this is at the top of the script.

Then just run the script. It takes about 1 second per book on the first run through. Subsequent runs, for picking up new entries, are about twice as fast for existing items.

##Limitations

This has only been tested on a Mint Linux machine as I don't have a windows box with Calibre on it.

This has only been tested with Python 3.12


There may well be edge conditions, especially for non-english items, that I haven't found. You are strongly advised to make a backup of KoboReader.sqlite, at least, before trying this.