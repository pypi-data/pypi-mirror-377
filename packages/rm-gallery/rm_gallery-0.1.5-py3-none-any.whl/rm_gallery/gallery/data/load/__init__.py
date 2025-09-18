from rm_gallery.gallery.data.annotation.rewardbench import RewardBenchAnnotationTemplate
from rm_gallery.gallery.data.annotation.rewardbench2 import (
    RewardBench2AnnotationTemplate,
)
from rm_gallery.gallery.data.load.helpsteer2_pairwise import HelpSteer2PairwiseConverter
from rm_gallery.gallery.data.load.helpsteer2_pointwise import (
    HelpSteer2PointwiseConverter,
)
from rm_gallery.gallery.data.load.judgebench import JudgeBenchConverter
from rm_gallery.gallery.data.load.prmbench import PRMBenchConverter
from rm_gallery.gallery.data.load.rewardbench import RewardBenchConverter
from rm_gallery.gallery.data.load.rewardbench2 import RewardBench2Converter
from rm_gallery.gallery.data.load.rmbbenchmark_bestofn import (
    RMBBenchmarkBestOfNConverter,
)
from rm_gallery.gallery.data.load.rmbbenchmark_pairwise import (
    RMBBenchmarkPairwiseConverter,
)
from rm_gallery.gallery.data.load.rmbench import RMBenchConverter

LOAD_STRATEGIES = {
    "rewardbench": RewardBenchConverter,
    "prmbench": PRMBenchConverter,
    "helpsteer2_pointwise": HelpSteer2PointwiseConverter,
    "helpsteer2_pairwise": HelpSteer2PairwiseConverter,
    "rewardbench2": RewardBench2Converter,
    "rmbbenchmark_bestofn": RMBBenchmarkBestOfNConverter,
    "rmbbenchmark_pairwise": RMBBenchmarkPairwiseConverter,
    "rmbench": RMBenchConverter,
    "judgebench": JudgeBenchConverter,
}

ANNOTATION_TEMPLATES = {
    "rewardbench": RewardBenchAnnotationTemplate,
    "rewardbench2": RewardBench2AnnotationTemplate,
}
