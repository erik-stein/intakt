DESC = "desc"
COST_CENTERS = "cost_centers"

DATA = {
    "aktu": {
        DESC: "IR AktU Zettle",
    },
    "cafe": {
        DESC: "IR Caféverksamhet",
        COST_CENTERS: {
            3000: "CAFE02",
            3020: "CAFE01",
        },
    },
    "dchip": {
        DESC: "IR D-Chip",
    },
    "dshop": {
        DESC: "IR D-Shopen Zettle",
        COST_CENTERS: {
            3000: "AKTU02",
        },
    },
    "medalj": {
        DESC: "IR Medaljelelekommiténs versamhet",
        COST_CENTERS: {
            3000: "MED01",
        },
    },
    "noll": {
        DESC : "IR NollU",
    },
    "skatt": {
        DESC: "IR Skattmästeriet (övriga intäkter)",
    },
    "sex": {
        DESC: "IR Sexmästeriet",
    },
    "uted" : {
        DESC: "IR UteDischot",
        COST_CENTERS: {
            3010: "SEX09",
            3011: "SEX09",
            3012: "SEX09",
            3013: "SEX09",
            3014: "SEX09",
            3015: "AKTU03",
        },
    },
}

ACCOUT_ZETTLE = 1919
ACCOUT_SWISH = 1933

VOUCHER_SERIES = "A"
