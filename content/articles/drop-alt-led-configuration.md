---
title: "Drop ALT led configuration using bitmask"
date: 2020-08-23T12:23:13+02:00
lang: en
taxonomies:
  tags: []
extra:
  sources: []
  footnotes: []
---

I recently purchased an [ALT mechanical keyboard](https://drop.com/buy/drop-alt-high-profile-mechanical-keyboard) from Drop (formerly Massdrop).

After going through the mandatory modding (changing _Halo Trues_ for _Aliaz_ switches, changing stabilizers, lubbing what needed to be lubed, etc...), I started compiling and flashing my own custom [QMK firmware](https://github.com/qmk/qmk_firmware). It worked pretty great, but I was stuck at backlight configuration. I could not understand or guess how to configure it.

I ended up [reading code](https://github.com/qmk/qmk_firmware/blob/master/keyboards/massdrop/alt/config_led.h#L52-L169) and [examples](https://github.com/qmk/qmk_firmware/blob/master/keyboards/massdrop/alt/keymaps/default_md/keymap.c#L183-L221) provided by QMK. The keyboard is built upon a 105 LED matrix.

A particular example caught my attention : 

```c,linenos
//Specific LEDs use specified RGB values while all others are off
{ .flags = LED_FLAG_MATCH_ID | LED_FLAG_USE_RGB, \
    .id0 = 0xFF, \
    .id1 = 0x00FF, \
    .id2 = 0x0000FF00, \
    .id3 = 0xFF000000, \
      .r = 75, \
      .g = 150, \
      .b = 225 \
},
```

And it struck me ! Bitmask ! The only thing that can select -- at the same time -- both a single address and multiple ones is a _bitmask_ !

By converting hexadecimal values to decimal, we get familiar-looking numbers. They belong to the [_successive power of two_](https://en.wikipedia.org/wiki/1_%2B_2_%2B_4_%2B_8_%2B_%E2%8B%AF) serie :

$$
\mathrm{0xFF} = 255 = 1 + 2 + 4 + 8 + 16 + 32 + 64 + 128 = \displaystyle\sum_{i=0}^{7} 2^{i}
$$

$$
\mathrm{0x0000FF00} = 65280 = 1 + 2 + \ldots = \displaystyle\sum_{i=8}^{15} 2^{i}
$$

$$
\mathrm{0xFF000000} = 4278190080 = 16 777 216 + 33 554 432 + \ldots = \displaystyle\sum_{i=24}^{31} 2^{i}
$$

The keyboard is separated in 4 groups of 32 LEDs (except the last one of 9 LEDs) :

* `.id0`: from `Esc` to `a`
* `.id1`: from `s` to `fn`
* `.id2`: from `Left Arrow` to _Underglow LED above `5`_
* `.id3`: from _Underglow LED above `4`_ to the end (_Underglow LED left of `Ctrl`_)

Each LED is assigned a number from `0` to `31` based on its position in the group.

Let say we want to display a green color on the first four letters of every row (`Q(16)`, `W(17)`, `E(18)`, `R(19)`, `A(31)`, `S(0)`, `D(1)`, `F(2)`, `Z(13)`, `X(14)`, `C(15)`, `V(16)`). We just need to add every value as a power of two : 

$$ .id0 = 2^{16} + 2^{17} + 2^{18} + 2^{19} + 2^{31} = 2 148 466 688 $$
$$ .id1 = 2^0 + 2^1 + 2^2 + 2^{13} + 2^{14} + 2^{15} + 2^{16} = 122 887 $$

And we get :

```c,linenos
{ .flags = LED_FLAG_MATCH_ID | LED_FLAG_USE_RGB, \
    .id0 = 2148466688, \
    .id1 = 122887, \
    .id2 = 0, \
    .id3 = 0, \
    .r = 0, \
    .g = 255, \
    .b = 0, \
},
```

While being a smart way to target both one and multiple LEDs, it's not very easy to understand and even less to change.

Fortunately, someone very nice created a bitmask generator [online](http://daedalusrising.com/maskdrop/).