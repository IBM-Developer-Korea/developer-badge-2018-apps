import ugfx

wb = ugfx.Style(ugfx.Font('IBMPlexSans_Regular22'))

wb.set_background(ugfx.BLACK)
wb.set_focus(ugfx.WHITE)
wb.set_pressed([
    ugfx.WHITE,
    ugfx.WHITE,
    ugfx.BLACK,
    ugfx.BLACK,
])
wb.set_enabled([
    ugfx.WHITE,
    ugfx.WHITE,
    ugfx.BLACK,
    ugfx.BLACK,
])
wb.set_disabled([
    ugfx.WHITE,
    ugfx.WHITE,
    ugfx.BLACK,
    ugfx.BLACK,
])

ibm_st = ugfx.Style(ugfx.Font('IBMPlexMono_Bold24'))

ibm_st.set_background(ugfx.HTML2COLOR(0x3c3c3b))
ibm_st.set_focus(ugfx.HTML2COLOR(0x01d7dd))
ibm_st.set_pressed([
    ugfx.WHITE, # Text
    ugfx.WHITE, # Edge
    ugfx.BLACK, # Fill
    ugfx.BLACK, # Progress
])
ibm_st.set_enabled([
    ugfx.WHITE,
    ugfx.WHITE,
    ugfx.HTML2COLOR(0x01d7dd),
    ugfx.BLACK,
    #ugfx.HTML2COLOR(0x3c3c3b),
])
ibm_st.set_disabled([
    ugfx.WHITE,
    ugfx.WHITE,
    ugfx.BLACK,
    ugfx.BLACK,
])
