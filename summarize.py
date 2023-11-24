# scrap the review
# python for pupetteer
from pyppeteer import launch
import google.generativeai as palm
import asyncio

import config

# T55 patisserie
url =  "https://www.google.com/maps/place/T55+P%C3%A2tisserie/@47.7605698,-122.2106145,17z/data=!4m8!3m7!1s0x54900fa03e68eec3:0x53a7c614f6b311ef!8m2!3d47.7605662!4d-122.2080396!9m1!1b1!16s%2Fg%2F11q4hv8_0l?entry=ttu"
async def scrape_view(url):
    reviews =  []
    browser = await launch(executablePath="/usr/bin/google-chrome", headless=False)

    page = await browser.newPage()
    await page.setViewport({"width":800, "height": 3200 })
    await page.goto(url)
    await page.waitForSelector(".jftiEf")

    elements = await page.querySelectorAll(".jftiEf")
    for element in elements:
        try:
            await page.waitForSelector(".w8nwRe")
            more_button = await element.querySelector(".w8nwRe")
            if more_button is not None:
                await page.evaluate('(element) => element.click()', more_button)
                await page.waitFor(5000)
        except:
            # Ignore exception
            pass
        await page.waitForSelector(".MyEned")
        snippet = await element.querySelector(".MyEned")
        text = await page.evaluate('selected => selected.textContent', snippet)
        reviews.append(text)
    
    await browser.close()
    return reviews

# output recommended dishes
def summarize(reviews, model):
    prompt = "I collect some reviews of a place I want to visit, can you recommend the top 5 dishes and list how many times each of which is mentioned?\
    the reviews are: \n"
    for review in reviews:
        prompt = prompt + "\n" + review

    #print(prompt)
    
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        # higher temperature == more randomness
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,
    )

    print(completion.result)


palm.configure(api_key = config.API_KEY)
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name
print(model)

reviews = asyncio.get_event_loop().run_until_complete(scrape_view(url))
print(reviews)

summary = summarize(reviews, model)
