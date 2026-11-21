#!/usr/bin/env python3
"""Build original social-image variants from a licensed/project-created source image.

Authoring helper only; the site itself needs only the raster files. Source image
is retained in static/assets for reproducibility with Python and Pillow.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'static/assets/social-field-source.jpg'
DEST=ROOT/'static/assets'
OUTW,OUTH=1200,630
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
SANS_BOLD='/usr/share/fonts/opentype/inter/Inter-Bold.otf'

variants={
 'home':(('Satellite signals','can be jammed.','Gravity can\'t.'),'INSTRUMENTS   /   EVIDENCE   /   NAVIGATION'),
 'instruments':(('Instrument families.','Evidence before','claims.'),'SOURCE-LINKED   /   GRAVITY INSTRUMENT ATLAS'),
 'navigation':(('When GNSS','goes silent,','gravity remains.'),'NAVIGATION EVIDENCE   /   NOT PROMISES'),
 'acquisition':(('A category name.','A verifiable','transfer.'),'STRATEGIC ACQUISITION   /   CLEAR PROCESS'),
}

def create(name, lines, sub):
    base=Image.open(SRC).convert('RGB')
    # Crop original to the social-sharing aspect ratio.
    width,height=base.size
    target_ratio=OUTW/OUTH
    crop_h=int(width/target_ratio)
    if crop_h>height:
        crop_w=int(height*target_ratio);x0=(width-crop_w)//2
        base=base.crop((x0,0,x0+crop_w,height))
    else:
        y0=(height-crop_h)//2
        base=base.crop((0,y0,width,y0+crop_h))
    base=base.resize((OUTW,OUTH),Image.Resampling.LANCZOS)
    base=ImageEnhance.Contrast(base).enhance(1.05)
    d=ImageDraw.Draw(base,'RGBA')
    # Protect legibility of text and keep all visuals secondary to the domain.
    for x in range(0,940,4):
        frac=x/940
        alpha=round(238*(1-frac)**2)
        d.rectangle((x,0,x+4,OUTH),fill=(1,16,24,alpha))
    d.rectangle((49,52,1151,574),outline=(136,221,223,80),width=1)
    d.line((65,125,290,125),fill=(135,226,220,220),width=2)
    label=ImageFont.truetype(SANS_BOLD,24)
    serif=ImageFont.truetype(SERIF,57)
    fine=ImageFont.truetype(SANS,15)
    d.text((65,80),'GRAVIMETERS.COM',font=label,fill=(169,237,229,255),spacing=0)
    yy=188
    for i,line in enumerate(lines):
        d.text((65,yy),line,font=serif,fill=(140,234,217,255) if i==2 else (251,248,241,255),stroke_width=0)
        yy+=77
    d.text((67,548),sub,font=fine,fill=(189,209,211,255))
    d.text((1086,548),'G / 01',font=fine,fill=(191,213,214,255))
    output=DEST/f'og-{name}.jpg'
    base.save(output,format='JPEG',quality=87,subsampling=0,optimize=True)
    print(name,output.stat().st_size)

if __name__=='__main__':
    for name,(lines,sub) in variants.items():create(name,lines,sub)
