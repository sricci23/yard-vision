3/3/15:

Made major alterations to simple-ocr; added functionality to use the Tesseract OCR library instead of the default OCR algorithm.

New command line arguments:

--tesseract	If supplied, use Tesseract for OCR.
--tesslangpath	Location of the tessdata folder in your Tesseract installation.
--terse		If provided, skips the final character display step. Intended for bulk analysis.

If the program is run using Tesseract, it will look for a master ground truth file named CroppedMasterIDs.csv. (TODO: Make this a command-line argument.) This contains the file names and the correct container codes. The Tesseract analysis uses Prim's algorithm to find clusters of 10 segments, then uses each segment's position in the cluster to generate a whitelist to pass to Tesseract. It then runs Tesseract for each segment in single-character mode. Once this is done, it iterates through the images and builds a code string from the characters in each cluster, then compares them to the ground truth file. It finally outputs the results to OCROutput.csv, along with a match percentage.