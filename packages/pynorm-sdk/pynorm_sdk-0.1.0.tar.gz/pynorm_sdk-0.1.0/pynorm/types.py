from enum import Enum


class RxNormPropertyName(str, Enum):
    ACTIVATED = "ACTIVATED"
    ANADA = "ANADA"
    ANDA = "ANDA"
    AVAILABLE_STRENGTH = "AVAILABLE_STRENGTH"
    BLA = "BLA"
    BN_CARDINALITY = "BN_CARDINALITY"
    CVX = "CVX"
    DRUGBANK = "DRUGBANK"
    GENERAL_CARDINALITY = "GENERAL_CARDINALITY"
    HUMAN_DRUG = "HUMAN_DRUG"
    IN_EXPRESSED_FLAG = "IN_EXPRESSED_FLAG"
    MMSL_CODE = "MMSL_CODE"
    NADA = "NADA"
    NDA = "NDA"
    NHRIC = "NHRIC"
    ORIG_CODE = "ORIG_CODE"
    ORIG_SOURCE = "ORIG_SOURCE"
    PRESCRIBABLE = "PRESCRIBABLE"
    PRESCRIBABLE_SYNONYM = "Prescribable Synonym"
    QUALITATIVE_DISTINCTION = "QUALITATIVE_DISTINCTION"
    QUANTITY = "QUANTITY"
    RXNAV_HUMAN_DRUG = "RXNAV_HUMAN_DRUG"
    RXNAV_STR = "RXNAV_STR"
    RXNAV_VET_DRUG = "RXNAV_VET_DRUG"
    RxCUI = "RxCUI"
    RxNormName = "RxNormName"
    RxNormSynonym = "RxNorm Synonym"
    SCHEDULE = "SCHEDULE"
    SPL_SET_ID = "SPL_SET_ID"
    STRENGTH = "STRENGTH"
    Source = "Source"
    TTY = "TTY"
    TallmanSynonym = "Tallman Synonym"
    UNII_CODE = "UNII_CODE"
    USP = "USP"
    VET_DRUG = "VET_DRUG"
    VUID = "VUID"


class RxNormIdType(str, Enum):
    AMPID = "AMPID"
    ANADA = "ANADA"
    ANDA = "ANDA"
    ATC = "ATC"
    BLA = "BLA"
    CVX = "CVX"
    DRUGBANK = "DRUGBANK"
    GCN_SEQNO = "GCN_SEQNO"
    GFC = "GFC"
    HCPCS = "HCPCS"
    HIC_SEQNO = "HIC_SEQNO"
    MMSL_CODE = "MMSL_CODE"
    NADA = "NADA"
    NDA = "NDA"
    NDC = "NDC"
    NHRIC = "NHRIC"
    SNOMEDCT = "SNOMEDCT"
    SPL_SET_ID = "SPL_SET_ID"
    UNII_CODE = "UNII_CODE"
    USP = "USP"
    VUID = "VUID"


class RxNormSourceType(str, Enum):
    ATC = "ATC"
    CVX = "CVX"
    DRUGBANK = "DRUGBANK"
    GS = "GS"
    MDDB = "MDDB"
    MMSL = "MMSL"
    MMX = "MMX"
    MSH = "MSH"
    MTHCMSFRF = "MTHCMSFRF"
    MTHSPL = "MTHSPL"
    NDDF = "NDDF"
    RXNORM = "RXNORM"
    SNOMEDCT_US = "SNOMEDCT_US"
    USP = "USP"
    VANDF = "VANDF"


class RxNormTermType(str, Enum):
    BN = "BN"  # Brand Name
    BPCK = "BPCK"  # Branded Pack
    DF = "DF"  # Dose Form
    DFG = "DFG"  # Dose Form Group
    GPCK = "GPCK"  # Generic Pack
    IN = "IN"  # Ingredient
    MIN = "MIN"  # Multiple Ingredient
    PIN = "PIN"  # Precise Ingredient
    SBD = "SBD"  # Semantic Branded Drug
    SBDC = "SBDC"  # Semantic Branded Drug Component
    SBDF = "SBDF"  # Semantic Dose Form
    SBDFP = "SBDFP"  # Semantic Dose Form Pack
    SBDG = "SBDG"  # Semantic Dose Form Group
    SCD = "SCD"  # Semantic Clinical Drug
    SCDC = "SCDC"  # Semantic Clinical Drug Component
    SCDF = "SCDF"  # Semantic Clinical Drug Form
    SCDFP = "SCDFP"  # Semantic Clinical Drug Form Pack
    SCDG = "SCDG"  # Semantic Clinical Drug Group
    SCDGP = "SCDGP"  # Semantic Clinical Drug Group Pack


class RxNormPropertyCategory(str, Enum):
    ATTRIBUTES = "ATTRIBUTES"
    CODES = "CODES"
    NAMES = "NAMES"
    SOURCES = "SOURCES"


class RxNormRelationshipType(str, Enum):
    boss_of = "boss_of"
    consists_of = "consists_of"
    constitutes = "constitutes"
    contained_in = "contained_in"
    contains = "contains"
    dose_form_of = "dose_form_of"
    doseformgroup_of = "doseformgroup_of"
    form_of = "form_of"
    has_boss = "has_boss"
    has_dose_form = "has_dose_form"
    has_doseformgroup = "has_doseformgroup"
    has_form = "has_form"
    has_ingredient = "has_ingredient"
    has_ingredients = "has_ingredients"
    has_part = "has_part"
    has_precise_ingredient = "has_precise_ingredient"
    has_quantified_form = "has_quantified_form"
    has_tradename = "has_tradename"
    ingredient_of = "ingredient_of"
    ingredients_of = "ingredients_of"
    inverse_isa = "inverse_isa"
    isa = "isa"
    part_of = "part_of"
    precise_ingredient_of = "precise_ingredient_of"
    quantified_form_of = "quantified_form_of"
    reformulated_to = "reformulated_to"
    reformulation_of = "reformulation_of"
    tradename_of = "tradename_of"