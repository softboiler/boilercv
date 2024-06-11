"""Theoretical correlations for bubble lifetimes."""

SYMBOLS = {
    "Nu_c": "nusselt",
    "Fo_0": "bubble_fourier",
    "Ja": "bubble_jakob",
    "Re_b": "bubble_reynolds",
    "Re_b0": "bubble_initial_reynolds",
    "Pr": "liquid_prandtl",
    "beta": "beta",
    "alpha": "thermal_diffusivity",
    "pi": "pi",
}

GROUPS = {
    k: f"Group {v}"
    for k, v in {
        "florschuetz_chao_1965": 1,
        "isenberg_sideman_1970": 3,
        "akiyama_1973": 3,
        "chen_mayinger_1992": 3,
        "zeitoun_et_al_1995": 5,
        "kalman_mori_2002": 3,
        "warrier_et_al_2002": 4,
        "yuan_et_al_2009": 4,
        "lucic_mayinger_2010": 3,
        "kim_park_2011": 3,
        # "inaba_et_al_2013": 5,
        "al_issa_et_al_2014": 3,
        "tang_et_al_2016": 3,
    }.items()
}
