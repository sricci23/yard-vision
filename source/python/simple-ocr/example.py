from files import ImageFile, get_image_filenames, find_image_file
import opencv_utils
from segmentation import MinContourSegmenter, ContourSegmenter
from feature_extraction import SimpleFeatureExtractor
from classification import KNNClassifier
from ocr import OCR, accuracy, show_differences, reconstruct_chars
from grounding import UserGrounder, TextGrounder
import tesseract


if __name__ == '__main__':
    print __doc__

    import argparse

    parser = argparse.ArgumentParser(description="Load training data and attempt OCR on some files.")
    parser.add_argument('--verbose', help='show intermediate steps', action="store_true")
    parser.add_argument('--retrain', help='regenerate training data''s ground truth from scratch', action="store_true")
    parser.add_argument('--trainfile', help='training data', type=str, nargs="+", default=[])
    parser.add_argument('--dir', help='directory of files to classify', default='yard_images')
    parser.add_argument('--file', help='file to classify', type=str, nargs="*", default=[])
    parser.add_argument('--tesseract', help='use tesseract for OCR', action='store_true')
    parser.add_argument('--tesslangpath', help='file path for tesseract', type=str)
    args = parser.parse_args()

    verbose = args.verbose
    force_train = args.retrain
    use_tesseract = args.tesseract
    tesslangpath = args.tesslangpath

    segmenter = MinContourSegmenter(blur_y=5, blur_x=5, min_width=5, block_size=17, c=6, max_ratio=4.0)
    extractor = SimpleFeatureExtractor(feature_size=10, stretch=False)
    classifier = KNNClassifier(k=3 )
    ocr = OCR(segmenter, extractor, classifier)

    for file_to_train in args.trainfile:
        training_image = ImageFile(file_to_train)
        if not training_image.isGrounded() or force_train:
            #trainingsegmenter = ContourSegmenter(blur_y=1, blur_x=1, min_width=3, min_height=15, max_height=50, min_area=30, block_size=23, c=3) # tweaked for black font
            trainingsegmenter = ContourSegmenter(blur_y=1, blur_x=1, min_width=3, min_height=15, max_height=50, min_area=30, block_size=3 , c=5, nearline_tolerance=10.0   ) # tweaked for white font
            segments = trainingsegmenter.process(training_image.image)
            if verbose:
                trainingsegmenter.display()

            # grounder = UserGrounder()   # interactive version; lets the user review, assign ground truth data
            grounder = TextGrounder()   # non-interactive ground-truth - assumes clean, ordered input
            grounder.ground(training_image, segments, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # writes out a .box file of image ground truths


        ocr.train(training_image)

    # Classify given image(s) using training data
    test_images = []
    if args.file != None and len(args.file) > 0:
        for file_to_classify in args.file:
            img = find_image_file(file_to_classify)
            if img:
                test_images.append(img)
    elif args.dir != None:
        test_images = get_image_filenames(args.dir)
    else:
        raise Exception("Need --dir [directory] or [--file <image> ..]")
    
    if (use_tesseract):
        api = tesseract.TessBaseAPI()
        api.Init(tesslangpath, "eng", tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
        api.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # classify
    for fname in test_images:
        test_image = ImageFile(fname)
        test_classes, test_segments = ocr.ocr(test_image, show_steps=verbose)
        if (use_tesseract):
            tesseract_image = tesseract.pixRead(fname)
            api.SetImage(tesseract_image)
            tesseract_classes = []
            for segment in test_segments:
                api.SetRectangle(int(segment[0]), int(segment[1]), int(segment[2]), int(segment[3]))
                text = api.GetUTF8Text()[0]
                tesseract_classes.append(text)
            test_classes = tesseract_classes
        image = test_image.image.copy()
        opencv_utils.draw_segments(image, test_segments, color=(255, 0, 0), line_width=1)
        opencv_utils.draw_classes(image, test_segments, test_classes, color=(255, 255, 0), line_width=2)

        opencv_utils.show_image_and_wait_for_key(image, "OCR results for file " + fname)

        if test_image.isGrounded():
            print "accuracy:", accuracy(test_image.ground.classes, test_classes)
            print "OCRed text:\n", reconstruct_chars(test_classes)
            show_differences(test_image.image, test_segments, test_image.ground.classes, test_classes)
    
    if (use_tesseract):
        api.End()
