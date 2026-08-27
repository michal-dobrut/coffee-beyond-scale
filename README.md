# coffee-beyond-scale

Every brewing method starts with "Weigh X g of coffee beans..." but what if you left your digital scale at home? As usual, math to the rescue!

There are big and small beans. But _on average_, an example roasted Arabica bean weighs 0.145 g with a standard deviation of 0.022 g.

We are measuring a dose of 100 beans.

$SD_{sum} = SD \cdot \sqrt{n}$

so its standard deviation is only 10x bigger (0.22 g) than that of a single bean. Or, with 95% probability, you'll have 14.5 g $\pm$ 0.43 g by just counting beans. That's only 3% error - enough for a tasty espresso!*

*What if you haven't measured SD of your beans? Well, I'll predict it!

## Approach(es)

First, spread your beans over a white paper sheet of known size, A4 (ISO 216) for starters. Take a photo and process with a pipeline of choice. Each begins with unwarping of perspective based on paper edges, but what happens next... here I am to find out!

### Coffee-Coloured Area

Easiest way first - count coffee-brown pixels and multiply by the area-to-weight ratio.

### Classic Segmentation

Apply classic image operations until we can count individual beans reliably. Then multiply by average bean weight.

### YOLO

Neural nets are still hot, so I'm not skipping this. Steps are:
1. collect enough data
2. annotate
3. train
4. celebrate being 0.4% better than classical methods

## Side-Track Experiments

I'll start with the same jar of coffee for pipeline validation. But for the method to be usable, some calibration against roast level and bean size will increase precision to a usable state.

Also, there is useful information in the camera's focal length and angle towards the surface - yup, I haven't missed it, patience advised!