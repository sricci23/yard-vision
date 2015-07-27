from files import ImageFile, get_image_filenames, find_image_file
import opencv_utils
from segmentation import MinContourSegmenter, ContourSegmenter
from feature_extraction import SimpleFeatureExtractor
from classification import KNNClassifier
from ocr import OCR, accuracy, show_differences, reconstruct_chars
from grounding import UserGrounder, TextGrounder
import tesseract
import tesseract_utils
import prim
from operator import itemgetter
from collections import OrderedDict
import os


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
    parser.add_argument('--terse', help='skip user prompts', action="store_true")
    args = parser.parse_args()

    verbose = args.verbose
    terse = args.terse
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
    dummy_name = args.dir + "\\dummy.jpg"
    if os.path.isfile(dummy_name):
        os.remove(dummy_name)
    if args.file != None and len(args.file) > 0:
        for file_to_classify in args.file:
            img = find_image_file(file_to_classify)
            if img:
                test_images.append(img)
    elif args.dir != None:
        test_images = get_image_filenames(args.dir)
    else:
        raise Exception("Need --dir [directory] or [--file <image> ..]")
    
    if use_tesseract:
        api = tesseract.TessBaseAPI()
        api.Init(tesslangpath, "eng", tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)        
        api.SetVariable("classify_enable_learning", "0")
        api.SetVariable("classify_enable_adaptive_matcher", "0")
        
    image_dict = OrderedDict()
    segment_text_list = []
    cluster_pattern_list = []

    # classify
    for fname in test_images:
        test_image = ImageFile(fname)
        test_classes, test_segments = ocr.ocr(test_image, show_steps=verbose)
        if use_tesseract:
            tesseract_image = tesseract.pixRead(fname)
            tesseract_classes = []
            cluster_list = []
            for segment in test_segments:
                cluster_segments = prim.get_cluster(segment, test_segments)
                if len(cluster_segments) == 10:
                    add = True
                    for list_cluster in cluster_list:
                        add = add and not tesseract_utils.is_cluster_match(cluster_segments, list_cluster)
                        if not add:
                            break
                    if add:
                        cluster_list.append(cluster_segments)
                pattern = tesseract_utils.get_pattern(cluster_segments)
                cluster_pattern_list.append([cluster_segments, pattern])
                whitelist = tesseract_utils.get_whitelist(segment, cluster_segments, pattern)
                api.SetVariable("tessedit_char_whitelist", whitelist)
                opencv_utils.create_dummy_image(fname, segment, dummy_name)
                api.SetImage(tesseract.pixRead(dummy_name))
                text = " "
                result = api.GetUTF8Text()
                if len(result) > 0:
                    text = result[0]
                if text == " ":
                    if len(whitelist) == 10:
                        text = "#"
                    elif len(whitelist) == 2 or len(whitelist) == 26:
                        text = "*"
                    else:
                        text = "?"
                segment_text_list.append([segment, text])
                tesseract_classes.append(text)
            test_classes = tesseract_classes
            image_dict[fname] = cluster_list
        if not terse:
            image = test_image.image.copy()
            opencv_utils.draw_segments(image, test_segments, color=(255, 0, 0), line_width=2)
            opencv_utils.draw_classes(image, test_segments, test_classes, color=(255, 255, 0), line_width=2)
    
            opencv_utils.show_image_and_wait_for_key(image, "OCR results for file " + fname)

            if test_image.isGrounded():
                print "accuracy:", accuracy(test_image.ground.classes, test_classes)
                print "OCRed text:\n", reconstruct_chars(test_classes)
                show_differences(test_image.image, test_segments, test_image.ground.classes, test_classes)
    
    if use_tesseract:
        api.End()
        
        ground_truth_dict = {}
        ground_truth_file = open("CroppedMasterIDs.csv", "r")
        for line in ground_truth_file:
            line = line.replace("\n", "")
            line_list = line.split(",")
            ground_truth_dict[args.dir + "\\" + line_list[0]] = line_list[1]
        ground_truth_file.close()
        output_list = []
        code_match_count = 0
        
        for image_name in image_dict:
            cluster_set = image_dict[image_name]
            image_code = ""
            max_match_count = 0
            for cluster in cluster_set:
                cluster_code = ""
                pattern = ""
                for cluster_pattern in cluster_pattern_list:
                    if tesseract_utils.is_cluster_match(cluster, cluster_pattern[0]):
                        pattern = cluster_pattern[1]
                        break
                if pattern == "H1":
                    h_sorted = sorted(cluster, key=itemgetter(0))
                    for segment in h_sorted:
                        text = ""
                        for segment_text in segment_text_list:
                            if (segment == segment_text[0]).all():
                                text = segment_text[1]
                                break
                        cluster_code = cluster_code + text
                elif pattern == "H2":
                    v_sorted = sorted(cluster, key=itemgetter(1))
                    prefix = v_sorted[:4]
                    prefix = sorted(prefix, key=itemgetter(0))
                    suffix = v_sorted[4:]
                    suffix = sorted(suffix, key=itemgetter(0))
                    for segment in prefix + suffix:
                        text = ""
                        for segment_text in segment_text_list:
                            if (segment == segment_text[0]).all():
                                text = segment_text[1]
                                break
                        cluster_code = cluster_code + text
                elif pattern == "V1":
                    v_sorted = sorted(cluster, key=itemgetter(1))
                    for segment in v_sorted:
                        text = ""
                        for segment_text in segment_text_list:
                            if (segment == segment_text[0]).all():
                                text = segment_text[1]
                                break
                        cluster_code = cluster_code + text
                elif pattern == "V2":
                    h_sorted = sorted(cluster, key=itemgetter(0))
                    prefix = h_sorted[:4]
                    prefix = sorted(prefix, key=itemgetter(1))
                    suffix = h_sorted[4:]
                    suffix = sorted(suffix, key=itemgetter(1))
                    for segment in prefix + suffix:
                        text = ""
                        for segment_text in segment_text_list:
                            if (segment == segment_text[0]).all():
                                text = segment_text[1]
                                break
                        cluster_code = cluster_code + text
                true_code = ground_truth_dict[image_name]
                if len(cluster_code) == len(true_code):
                    match_count = 0
                    for a, b in zip(true_code, cluster_code):
                        if a == b:
                            match_count = match_count + 1
                    if match_count > max_match_count:
                        max_match_count = match_count
                        image_code = cluster_code
                    if match_count >= 9:
                        image_code = true_code
                        code_match_count = code_match_count + 1
                        break
            output_list.append([image_name, true_code, image_code])
            
        output_file = open("OCROutput.csv", "w")
        output_file.write("File Name,True Code,OCR Code,Match %," + str(int(round(float(code_match_count) / len(output_list), 2) * 100)) + "%\n")
        for output in output_list:            
            output_file.write(output[0] + "," + output[1] + "," + output[2] + "\n")
        output_file.close()
