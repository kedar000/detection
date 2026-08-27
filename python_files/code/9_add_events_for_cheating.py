"""
Description:
    Modifies the files in modify_50 by injecting simulated shortcut
    activity and cheating-related browser events.

    For each file:
        1. Select exactly ONE shortcut key for the entire file.
        2. The shortcut key is selected using the Modified Probability
           distribution.
        3. The selected shortcut is used at least 5 times.
        4. Each shortcut use generates:
               KEY_DOWN(SHORTCUT)
               KEY_UP(SHORTCUT)
        5. The original typing events are never modified or removed.
        6. FOCUS_CHANGED and VISIBILITY_CHANGED are inserted sometimes
           after shortcut activity and sometimes independently.
        7. ANSWER_LENGTH_CHANGED is inserted at moderate/random
           positions.
        8. The final event order is preserved.
        9. Duplicate injected events are avoided at the same position.

    Input:
        ../keystroke_dataset/modify_50

    Output:
        ../keystroke_dataset/modified_cheating

    Note:
        The current files do not contain timestamps, so insertion is
        performed according to event-sequence position rather than
        timestamp.
"""

import os
import random
import shutil


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_FOLDER = "../keystroke_dataset/modify_50"

OUTPUT_FOLDER = "../keystroke_dataset/modified_cheating"


# ------------------------------------------------------------
# Minimum number of shortcut uses per file
# ------------------------------------------------------------

MIN_SHORTCUT_USES = 5


# ------------------------------------------------------------
# Maximum number of shortcut uses
#
# The actual number is selected based on file size.
# ------------------------------------------------------------

MAX_SHORTCUT_USES = 15


# ------------------------------------------------------------
# Custom event probabilities
# ------------------------------------------------------------

FOCUS_CHANGED_PROBABILITY = 0.35
VISIBILITY_CHANGED_PROBABILITY = 0.25
ANSWER_LENGTH_CHANGED_PROBABILITY = 0.30


# ------------------------------------------------------------
# Modified probabilities from your dataset
#
# Only keys that can reasonably act as modifier/shortcut keys
# are included in this first iteration.
# ------------------------------------------------------------

SHORTCUT_PROBABILITIES = {
    # "SHIFT": 0.135333,
    "CTRL": 0.000261,
    "ALT": 0.000109,
    "WIN": 0.000070,
    "HOME":0.000078,
    "MENU":0.000039
}


# ------------------------------------------------------------
# Reproducibility
#
# Change this number if you want a different dataset split.
# ------------------------------------------------------------

random.seed(42)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# SELECT SHORTCUT
# ============================================================

shortcut_keys = list(
    SHORTCUT_PROBABILITIES.keys()
)

shortcut_weights = list(
    SHORTCUT_PROBABILITIES.values()
)


def select_shortcut():
    """
    Select exactly one shortcut key using the modified
    probability distribution.
    """

    return random.choices(
        shortcut_keys,
        weights=shortcut_weights,
        k=1
    )[0]


# ============================================================
# NUMBER OF SHORTCUT USES
# ============================================================

def calculate_shortcut_count(event_count):
    """
    Determine how many times the selected shortcut should
    be used in a file.

    Every file gets at least 5 uses.

    Larger files can receive more shortcut activity.
    """

    if event_count < 100:
        maximum = 5

    elif event_count < 500:
        maximum = 7

    elif event_count < 1000:
        maximum = 10

    else:
        maximum = MAX_SHORTCUT_USES

    return random.randint(
        MIN_SHORTCUT_USES,
        maximum
    )


# ============================================================
# INSERT SHORTCUT EVENTS
# ============================================================

def insert_shortcuts(events, shortcut, count):
    """
    Insert shortcut KEY_DOWN / KEY_UP pairs at different
    positions throughout the original sequence.

    Original events are not changed.
    """

    if not events:
        return events

    result = events.copy()

    # Pick different positions when possible
    max_positions = min(
        count,
        len(result)
    )

    positions = sorted(
        random.sample(
            range(len(result)),
            max_positions
        ),
        reverse=True
    )

    for position in positions:

        shortcut_events = [
            f"KEY_DOWN({shortcut})",
            f"KEY_UP({shortcut})"
        ]

        result[position:position] = shortcut_events

    # If file is extremely small, make sure minimum shortcut
    # count is still satisfied.
    while count > max_positions:

        position = random.randint(
            0,
            len(result)
        )

        shortcut_events = [
            f"KEY_DOWN({shortcut})",
            f"KEY_UP({shortcut})"
        ]

        result[position:position] = shortcut_events

        max_positions += 1

    return result


# ============================================================
# INSERT CUSTOM EVENTS
# ============================================================

def insert_custom_events(events, shortcut):
    """
    Insert cheating-related custom events.

    FOCUS_CHANGED:
        Sometimes inserted after shortcut activity and
        sometimes at an independent random position.

    VISIBILITY_CHANGED:
        Same behavior as FOCUS_CHANGED.

    ANSWER_LENGTH_CHANGED:
        Inserted at a moderate/random position.
    """

    result = events.copy()

    # --------------------------------------------------------
    # Find shortcut locations
    # --------------------------------------------------------

    shortcut_positions = [
        i
        for i, event in enumerate(result)
        if event == f"KEY_DOWN({shortcut})"
    ]

    # --------------------------------------------------------
    # FOCUS_CHANGED
    # --------------------------------------------------------

    if random.random() < FOCUS_CHANGED_PROBABILITY:

        if shortcut_positions and random.random() < 0.6:

            # Place after a shortcut
            position = random.choice(
                shortcut_positions
            ) + 2

        else:

            # Independent random location
            position = random.randint(
                0,
                len(result)
            )

        result.insert(
            min(position, len(result)),
            "FOCUS_CHANGED"
        )

    # --------------------------------------------------------
    # VISIBILITY_CHANGED
    # --------------------------------------------------------

    if random.random() < VISIBILITY_CHANGED_PROBABILITY:

        if shortcut_positions and random.random() < 0.6:

            position = random.choice(
                shortcut_positions
            ) + 2

        else:

            position = random.randint(
                0,
                len(result)
            )

        result.insert(
            min(position, len(result)),
            "VISIBILITY_CHANGED"
        )

    # --------------------------------------------------------
    # ANSWER_LENGTH_CHANGED
    # --------------------------------------------------------

    if random.random() < ANSWER_LENGTH_CHANGED_PROBABILITY:

        # Avoid putting this immediately at the beginning/end
        if len(result) > 10:

            lower = int(len(result) * 0.2)
            upper = int(len(result) * 0.8)

            position = random.randint(
                lower,
                max(lower, upper)
            )

        else:

            position = random.randint(
                0,
                len(result)
            )

        result.insert(
            min(position, len(result)),
            "ANSWER_LENGTH_CHANGED"
        )

    return result


# ============================================================
# PROCESS FILE
# ============================================================

def process_file(input_path, output_path):

    # --------------------------------------------------------
    # Read original events
    # --------------------------------------------------------

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as infile:

        events = [
            line.rstrip("\n\r")
            for line in infile
            if line.strip()
        ]

    if not events:
        return {
            "original_events": 0,
            "shortcut": None,
            "shortcut_uses": 0,
            "final_events": 0
        }

    original_event_count = len(events)

    # --------------------------------------------------------
    # Select ONE shortcut for this entire file
    # --------------------------------------------------------

    shortcut = select_shortcut()

    # --------------------------------------------------------
    # Decide how many times to use it
    # --------------------------------------------------------

    shortcut_count = calculate_shortcut_count(
        original_event_count
    )

    # --------------------------------------------------------
    # Inject shortcuts
    # --------------------------------------------------------

    modified_events = insert_shortcuts(
        events,
        shortcut,
        shortcut_count
    )

    # --------------------------------------------------------
    # Inject custom cheating events
    # --------------------------------------------------------

    modified_events = insert_custom_events(
        modified_events,
        shortcut
    )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as outfile:

        for event in modified_events:
            outfile.write(
                event + "\n"
            )

    return {
        "original_events": original_event_count,
        "shortcut": shortcut,
        "shortcut_uses": shortcut_count,
        "final_events": len(modified_events)
    }


# ============================================================
# GET FILES
# ============================================================

files = sorted(
    filename
    for filename in os.listdir(SOURCE_FOLDER)
    if filename.endswith(".txt")
)


# ============================================================
# PROCESS DATASET
# ============================================================

print("=" * 70)
print("MODIFYING KEYSTROKE DATASET")
print("=" * 70)

print(f"Input:  {SOURCE_FOLDER}")
print(f"Output: {OUTPUT_FOLDER}")
print(f"Files:  {len(files)}")
print()


processed = 0
failed = 0

shortcut_usage = {}


for index, filename in enumerate(
    files,
    start=1
):

    input_path = os.path.join(
        SOURCE_FOLDER,
        filename
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    try:

        result = process_file(
            input_path,
            output_path
        )

        processed += 1

        shortcut = result["shortcut"]

        if shortcut:
            shortcut_usage[shortcut] = (
                shortcut_usage.get(shortcut, 0) + 1
            )

        print(
            f"[{index}/{len(files)}] "
            f"{filename} | "
            f"Shortcut={shortcut} | "
            f"Uses={result['shortcut_uses']} | "
            f"Events={result['original_events']} -> "
            f"{result['final_events']}"
        )

    except Exception as e:

        failed += 1

        print(
            f"[ERROR] {filename}: {e}"
        )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("MODIFICATION COMPLETE")
print("=" * 70)

print(f"Files processed: {processed}")
print(f"Files failed:    {failed}")

print()
print("Shortcut distribution:")

for key in shortcut_keys:

    print(
        f"  {key:<8}: "
        f"{shortcut_usage.get(key, 0)} files"
    )

print()
print(f"Output folder: {OUTPUT_FOLDER}")