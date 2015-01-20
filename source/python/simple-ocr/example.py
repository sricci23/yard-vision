from files import ImageFile, get_image_filenames, find_image_file
import opencv_utils
from segmentation import MinContourSegmenter, ContourSegmenter
from feature_extraction import SimpleFeatureExtractor
from classification import KNNClassifier
from ocr import OCR, accuracy, show_differences, reconstruct_chars
from grounding import UserGrounder, TextGrounder


if __name__ == '__main__':
    print __doc__

    import argparse

    parser = argparse.ArgumentParser(description="Load training data and attempt OCR on some files.")
    parser.add_argument('--verbose', help='show intermediate steps', action="store_true")
    parser.add_argument('--retrain', help='regenerate training data''s ground truth from scratch', action="store_true")
    parser.add_argument('--trainfile', help='training data', type=str, nargs="+", default=[])
    parser.add_argument('--dir', help='directory of files to classify', default='yard_images')
    parser.add_argument('--file', help='file to classify', type=str, nargs="*", default=[])
    args = parser.parse_args()

    verbose = args.verbose
    force_train = args.retrain

    segmenter = MinContourSegmenter(blur_y=5, blur_x=5, block_size=17, c=6, max_ratio=4.0)
    extractor = SimpleFeatureExtractor(feature_size=10, stretch=False)
    classifier = KNNClassifier(k=1 )
    ocr = OCR(segmenter, extractor, classifier)

    for file_to_train in args.trainfile:
        training_image = ImageFile(file_to_train)
        if not training_image.isGrounded() or force_train:
            trainingsegmenter = ContourSegmenter(blur_y=5, blur_x=5, block_size=23, c=3)
            segments = trainingsegmenter.process(training_image.image)
            if verbose:
                trainingsegmenter.display()
            grounder = TextGrounder()
            grounder.ground(training_image, segments, "0123456789")  # writes out a .box file of image ground truths

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

    # classify
    for fname in test_images:
        test_image = ImageFile(fname)
        test_classes, test_segments = ocr.ocr(test_image, show_steps=verbose)
        image = test_image.image.copy()
        opencv_utils.draw_segments(image, test_segments, color=(255, 0, 0), line_width=1)
        opencv_utils.draw_classes(image, test_segments, test_classes, color=(255, 255, 0), line_width=2)

        opencv_utils.show_image_and_wait_for_key(image, "OCR results for file " + fname)

        if test_image.isGrounded():
            print "accuracy:", accuracy(test_image.ground.classes, test_classes)
            print "OCRed text:\n", reconstruct_chars(test_classes)
            show_differences(test_image.image, test_segments, test_image.ground.classes, test_classes)
