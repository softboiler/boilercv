"""CINE file header model."""

from pydantic import BaseModel, Field

from boilercv_pipeline.models.header.types import FloatVec, IntVec


class CineHeader(BaseModel):
    """CINE file header."""

    exposure_time: float = Field(..., alias="ExposureTime")
    type: int = Field(..., alias="Type")
    headersize: int = Field(..., alias="Headersize")
    compression: int = Field(..., alias="Compression")
    version: int = Field(..., alias="Version")
    first_movie_image: int = Field(..., alias="FirstMovieImage")
    total_image_count: int = Field(..., alias="TotalImageCount")
    first_image_no: int = Field(..., alias="FirstImageNo")
    image_count: int = Field(..., alias="ImageCount")
    off_image_offsets: int = Field(..., alias="OffImageOffsets")
    trigger_time: str = Field(..., alias="TriggerTime")
    bi_size: int = Field(..., alias="BiSize")
    bi_width: int = Field(..., alias="BiWidth")
    bi_height: int = Field(..., alias="BiHeight")
    bi_planes: int = Field(..., alias="BiPlanes")
    bi_bit_count: int = Field(..., alias="BiBitCount")
    bi_compression: int = Field(..., alias="BiCompression")
    bi_size_image: int = Field(..., alias="BiSizeImage")
    bi_x_pels_per_meter: int = Field(..., alias="BiXPelsPerMeter")
    bi_y_pels_per_meter: int = Field(..., alias="BiYPelsPerMeter")
    bi_clr_used: int = Field(..., alias="BiClrUsed")
    bi_clr_important: int = Field(..., alias="BiClrImportant")
    trig_frame: int = Field(..., alias="TrigFrame")
    mark: int = Field(..., alias="Mark")
    length: int = Field(..., alias="Length")
    sig_option: int = Field(..., alias="SigOption")
    bin_channels: int = Field(..., alias="BinChannels")
    samples_per_image: int = Field(..., alias="SamplesPerImage")
    ana_option: int = Field(..., alias="AnaOption")
    ana_channels: int = Field(..., alias="AnaChannels")
    ana_board: int = Field(..., alias="AnaBoard")
    ch_option: IntVec = Field(..., alias="ChOption")
    ana_gain: FloatVec = Field(..., alias="AnaGain")
    l_first_image: int = Field(..., alias="LFirstImage")
    dw_image_count: int = Field(..., alias="DwImageCount")
    nq_factor: int = Field(..., alias="NQFactor")
    w_cine_file_type: int = Field(..., alias="WCineFileType")
    im_width: int = Field(..., alias="ImWidth")
    im_height: int = Field(..., alias="ImHeight")
    serial: int = Field(..., alias="Serial")
    auto_exposure: int = Field(..., alias="AutoExposure")
    b_flip_h: bool = Field(..., alias="BFlipH")
    b_flip_v: bool = Field(..., alias="BFlipV")
    frame_rate: int = Field(..., alias="FrameRate")
    grid: int = Field(..., alias="Grid")
    post_trigger: int = Field(..., alias="PostTrigger")
    b_enable_color: bool = Field(..., alias="BEnableColor")
    camera_version: int = Field(..., alias="CameraVersion")
    firmware_version: int = Field(..., alias="FirmwareVersion")
    software_version: int = Field(..., alias="SoftwareVersion")
    recording_time_zone: int = Field(..., alias="RecordingTimeZone")
    cfa: int = Field(..., alias="CFA")
    auto_exp_level: int = Field(..., alias="AutoExpLevel")
    auto_exp_speed: int = Field(..., alias="AutoExpSpeed")
    auto_exp_rect_left: int = Field(..., alias="AutoExpRectLeft")
    auto_exp_rect_top: int = Field(..., alias="AutoExpRectTop")
    auto_exp_rect_right: int = Field(..., alias="AutoExpRectRight")
    auto_exp_rect_bottom: int = Field(..., alias="AutoExpRectBottom")
    wb_gain0_r: float = Field(..., alias="WBGain0R")
    wb_gain0_b: float = Field(..., alias="WBGain0B")
    wb_gain1_r: float = Field(..., alias="WBGain1R")
    wb_gain1_b: float = Field(..., alias="WBGain1B")
    wb_gain2_r: float = Field(..., alias="WBGain2R")
    wb_gain2_b: float = Field(..., alias="WBGain2B")
    wb_gain3_r: float = Field(..., alias="WBGain3R")
    wb_gain3_b: float = Field(..., alias="WBGain3B")
    rotate: int = Field(..., alias="Rotate")
    wb_view_r: float = Field(..., alias="WBViewR")
    wb_view_b: float = Field(..., alias="WBViewB")
    real_bpp: int = Field(..., alias="RealBPP")
    filter_code: int = Field(..., alias="FilterCode")
    filter_param: int = Field(..., alias="FilterParam")
    uf_dim: int = Field(..., alias="UFDim")
    uf_shifts: int = Field(..., alias="UFShifts")
    uf_bias: int = Field(..., alias="UFBias")
    uf_coef: IntVec = Field(..., alias="UFCoef")
    black_cal_s_ver: int = Field(..., alias="BlackCalSVer")
    white_cal_s_ver: int = Field(..., alias="WhiteCalSVer")
    gray_cal_s_ver: int = Field(..., alias="GrayCalSVer")
    b_stamp_time: bool = Field(..., alias="BStampTime")
    sound_dest: int = Field(..., alias="SoundDest")
    frp_steps: int = Field(..., alias="FRPSteps")
    frp_img_nr: IntVec = Field(..., alias="FRPImgNr")
    frp_rate: IntVec = Field(..., alias="FRPRate")
    frp_exp: IntVec = Field(..., alias="FRPExp")
    mc_cnt: int = Field(..., alias="MCCnt")
    mc_percent: FloatVec = Field(..., alias="MCPercent")
    ci_calib: int = Field(..., alias="CICalib")
    calib_width: int = Field(..., alias="CalibWidth")
    calib_height: int = Field(..., alias="CalibHeight")
    calib_rate: int = Field(..., alias="CalibRate")
    calib_exp: int = Field(..., alias="CalibExp")
    calib_edr: int = Field(..., alias="CalibEDR")
    calib_temp: int = Field(..., alias="CalibTemp")
    head_serial: IntVec = Field(..., alias="HeadSerial")
    range_code: int = Field(..., alias="RangeCode")
    range_size: int = Field(..., alias="RangeSize")
    decimation: int = Field(..., alias="Decimation")
    master_serial: int = Field(..., alias="MasterSerial")
    sensor: int = Field(..., alias="Sensor")
    shutter_ns: int = Field(..., alias="ShutterNs")
    edr_shutter_ns: int = Field(..., alias="EDRShutterNs")
    frame_delay_ns: int = Field(..., alias="FrameDelayNs")
    im_pos_x_acq: int = Field(..., alias="ImPosXAcq")
    im_pos_y_acq: int = Field(..., alias="ImPosYAcq")
    im_width_acq: int = Field(..., alias="ImWidthAcq")
    im_height_acq: int = Field(..., alias="ImHeightAcq")
    rising_edge: bool = Field(..., alias="RisingEdge")
    filter_time: int = Field(..., alias="FilterTime")
    long_ready: bool = Field(..., alias="LongReady")
    shutter_off: bool = Field(..., alias="ShutterOff")
    b_meta_wb: bool = Field(..., alias="BMetaWB")
    black_level: int = Field(..., alias="BlackLevel")
    white_level: int = Field(..., alias="WhiteLevel")
    f_offset: float = Field(..., alias="FOffset")
    f_gain: float = Field(..., alias="FGain")
    f_saturation: float = Field(..., alias="FSaturation")
    f_hue: float = Field(..., alias="FHue")
    f_gamma: float = Field(..., alias="FGamma")
    f_gamma_r: float = Field(..., alias="FGammaR")
    f_gamma_b: float = Field(..., alias="FGammaB")
    f_flare: float = Field(..., alias="FFlare")
    f_pedestal_r: float = Field(..., alias="FPedestalR")
    f_pedestal_g: float = Field(..., alias="FPedestalG")
    f_pedestal_b: float = Field(..., alias="FPedestalB")
    f_chroma: float = Field(..., alias="FChroma")
    tone_points: int = Field(..., alias="TonePoints")
    f_tone: FloatVec = Field(..., alias="FTone")
    enable_matrices: bool = Field(..., alias="EnableMatrices")
    cm_user: FloatVec = Field(..., alias="CmUser")
    enable_crop: bool = Field(..., alias="EnableCrop")
    crop_rect_left: int = Field(..., alias="CropRectLeft")
    crop_rect_top: int = Field(..., alias="CropRectTop")
    crop_rect_right: int = Field(..., alias="CropRectRight")
    crop_rect_bottom: int = Field(..., alias="CropRectBottom")
    enable_resample: bool = Field(..., alias="EnableResample")
    resample_width: int = Field(..., alias="ResampleWidth")
    resample_height: int = Field(..., alias="ResampleHeight")
    f_gain16_8: float = Field(..., alias="FGain16_8")
    frp_shape: IntVec = Field(..., alias="FRPShape")


class CineHeaderPascal(BaseModel):
    """CINE file header with Phantom's original field names."""

    ExposureTime: FloatVec
    Type: int
    Headersize: int
    Compression: int
    Version: int
    FirstMovieImage: int
    TotalImageCount: int
    FirstImageNo: int
    ImageCount: int
    OffImageOffsets: int
    TriggerTime: str
    BiSize: int
    BiWidth: int
    BiHeight: int
    BiPlanes: int
    BiBitCount: int
    BiCompression: int
    BiSizeImage: int
    BiXPelsPerMeter: int
    BiYPelsPerMeter: int
    BiClrUsed: int
    BiClrImportant: int
    TrigFrame: int
    Mark: int
    Length: int
    SigOption: int
    BinChannels: int
    SamplesPerImage: int
    AnaOption: int
    AnaChannels: int
    AnaBoard: int
    ChOption: IntVec
    AnaGain: FloatVec
    LFirstImage: int
    DwImageCount: int
    NQFactor: int
    WCineFileType: int
    ImWidth: int
    ImHeight: int
    Serial: int
    AutoExposure: int
    BFlipH: bool
    BFlipV: bool
    FrameRate: int
    Grid: int
    PostTrigger: int
    BEnableColor: bool
    CameraVersion: int
    FirmwareVersion: int
    SoftwareVersion: int
    RecordingTimeZone: int
    CFA: int
    AutoExpLevel: int
    AutoExpSpeed: int
    AutoExpRectLeft: int
    AutoExpRectTop: int
    AutoExpRectRight: int
    AutoExpRectBottom: int
    WBGain0R: float
    WBGain0B: float
    WBGain1R: float
    WBGain1B: float
    WBGain2R: float
    WBGain2B: float
    WBGain3R: float
    WBGain3B: float
    Rotate: int
    WBViewR: float
    WBViewB: float
    RealBPP: int
    FilterCode: int
    FilterParam: int
    UFDim: int
    UFShifts: int
    UFBias: int
    UFCoef: IntVec
    BlackCalSVer: int
    WhiteCalSVer: int
    GrayCalSVer: int
    BStampTime: bool
    SoundDest: int
    FRPSteps: int
    FRPImgNr: IntVec
    FRPRate: IntVec
    FRPExp: IntVec
    MCCnt: int
    MCPercent: FloatVec
    CICalib: int
    CalibWidth: int
    CalibHeight: int
    CalibRate: int
    CalibExp: int
    CalibEDR: int
    CalibTemp: int
    HeadSerial: IntVec
    RangeCode: int
    RangeSize: int
    Decimation: int
    MasterSerial: int
    Sensor: int
    ShutterNs: int
    EDRShutterNs: int
    FrameDelayNs: int
    ImPosXAcq: int
    ImPosYAcq: int
    ImWidthAcq: int
    ImHeightAcq: int
    RisingEdge: bool
    FilterTime: int
    LongReady: bool
    ShutterOff: bool
    BMetaWB: bool
    BlackLevel: int
    WhiteLevel: int
    FOffset: float
    FGain: float
    FSaturation: float
    FHue: float
    FGamma: float
    FGammaR: float
    FGammaB: float
    FFlare: float
    FPedestalR: float
    FPedestalG: float
    FPedestalB: float
    FChroma: float
    TonePoints: int
    FTone: FloatVec
    EnableMatrices: bool
    CmUser: FloatVec
    EnableCrop: bool
    CropRectLeft: int
    CropRectTop: int
    CropRectRight: int
    CropRectBottom: int
    EnableResample: bool
    ResampleWidth: int
    ResampleHeight: int
    FGain16_8: float
    FRPShape: IntVec
