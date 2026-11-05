"""Shared state handed to every scene: rng, loaded art, glitch controller."""
import glob
import os
import random

from animations.anonymous_masks import MaskPair
from animations.glitch import Glitch
from animations.three_fingers import HandSprite
from core import config as cfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EXT = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp")


def find_asset(subdir):
    folder = os.path.join(ROOT, "assets", subdir)
    for pat in IMG_EXT:
        hits = sorted(glob.glob(os.path.join(folder, pat)))
        if hits:
            return hits[0]
    return None


class Context:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.warnings = []
        hand_path = find_asset("three_fingers")
        mask_path = find_asset("anonymous_masks")
        self.hand = HandSprite(hand_path)
        self.masks = MaskPair(mask_path)
        if self.hand.error:
            self.warnings.append("three-finger image: %s (using a placeholder)" % self.hand.error)
        if self.masks.error:
            self.warnings.append("mask image: %s (using a placeholder)" % self.masks.error)
        self.glitch = Glitch(self.rng)

    @property
    def motion(self):
        return cfg.motion()
