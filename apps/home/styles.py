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

ibm_st.set_background(ugfx.WHITE)
ibm_st.set_focus(ugfx.WHITE)
ibm_st.set_pressed([
    ugfx.BLACK, # Text
    ugfx.IBMCyan10, # Edge
    ugfx.BLACK, # Fill
    ugfx.BLACK, # Progress
])
ibm_st.set_enabled([
    ugfx.BLACK,
    ugfx.IBMCyan10,
    ugfx.IBMTeal30,
    ugfx.BLACK,
])
ibm_st.set_disabled([
    ugfx.GREY,
    ugfx.IBMCyan10,
    ugfx.IBMCoolGrey10,
    ugfx.BLACK,
])
