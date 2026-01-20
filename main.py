import langextract as lx
import textwrap
import networkx as nx
from pyvis.network import Network
import json

model_identifier = "llama3.1:8b"
local_model_url = "http://localhost:11434"


print("Starting extraction...")


# 1. Define the prompt and extraction rules

prompt = textwrap.dedent(
"""
Role: You are an agent that extracts financial information from text as it is.

Goal:
You will be provided with news or arrticles related to the finance of a company. Your task is to extract:
- Company Names
- Stock Tickers
- Financial Events (e.g., earnings reports, mergers, acquisitions)
- Dates of Events
- Relevant Financial Figures (e.g., revenue, profit, stock price changes)
- CEO Names
- Sentiment (positive, negative, neutral) regarding the financial events

Extract the following relationships:
- (Company) -> [ISSUES] -> (Ticker)
- (Company) -> [EXPERIENCED] -> (Financial Event)
- (Event) -> [HAPPENED_ON] -> (Date)
- (Event) -> [HAS_VALUE] -> (Financial Figure)
- (Company) -> [COMPETES_WITH] -> (Company)
- (Executive) -> [WORKS_FOR] -> (Company)

"""
)

# 2. Provide a high-quality example to guide the model
example_text = """
 NVIDIA Corporation’s NVDA stock

climbed 1% on Friday, Dec. 26, after it announced a strategic licensing

partnership with AI inference chipmaker Groq and the integration of key

Groq leadership into Nvidia’s teams. This was, in essence, further

evidence of Nvidia’s expanding role in artificial intelligence (AI)

infrastructure, especially beyond its core GPU training prowess. As

traders closed out a holiday-shortened week, Nvidia’s shares finished

the session at around $190.53.

Prediction Market powered by

Throughout

2025, NVDA, part of the Zacks Semiconductor - General industry, has

delivered robust gains amid surging global demand for AI hardware and

continued optimism about the company’s long-term growth trajectory.

Friday’s uptick came as Nvidia detailed its non-exclusive licensing

agreement with Groq, under which it will integrate Groq’s inference

technology into its portfolio and welcome Groq’s founder and other

senior personnel to help scale the licensed technology. While the deal

stops short of a full acquisition, the arrangement reinforces Nvidia’s

bet on bolstering its AI chip capabilities across both training and

inference workloads.

Nvidia’s year-end

strength reflects broader confidence in AI as a structural growth driver

for technology markets, even as macroeconomic and regulatory

uncertainties linger. While investors remained concerned about whether

AI is actually a bubble, the stock’s performance this year has outpaced

many peers in the semiconductor sector. This has aligned with sustained

investor appetite for companies positioned to benefit from the ongoing

AI-driven transformation of computing infrastructure.

Year

to date, NVDA’s shares have risen about 42% compared with the Zacks

sub-industry's growth of 38.6%, supported by strong earnings, expanding

data-center deployments and a series of partnerships and investments

that have reinforced its position at the heart of the AI boom. STMicroelectronics N.V. STM and Texas Instruments Incorporated TXN,

two of its peers from the same industry, have moved 5.1% and -5.7%,

respectively, in the same period. While NVDA has a Zacks #2 (Buy), both

STM and TXN carry a #3 (Hold). You can see the complete list of today’s Zacks #1 Rank (Strong Buy) stocks here.


Zacks Investment Research

Image Source: Zacks Investment Research

Bottom Line

As

Nvidia heads into 2026, its ability to leverage strategic partnerships

like the Groq deal, alongside continued innovation in next-generation

chips and AI platforms, will likely remain a focal point for the AI boom

and tech sector in general. 
"""


examples = [
    # Example 7: NVIDIA / Groq Strategic Partnership
    lx.data.ExampleData(
        text=example_text,
        extractions=[
            # Company Names
            lx.data.Extraction(extraction_class="company", extraction_text="NVIDIA Corporation", attributes={"type": "corporation"}),
            lx.data.Extraction(extraction_class="company", extraction_text="Groq", attributes={"type": "licensor"}),
            lx.data.Extraction(extraction_class="company", extraction_text="STMicroelectronics N.V.", attributes={"type": "peer"}),
            lx.data.Extraction(extraction_class="company", extraction_text="Texas Instruments Incorporated", attributes={"type": "peer"}),
            
            # Stock Tickers
            lx.data.Extraction(extraction_class="ticker", extraction_text="NVDA", attributes={"exchange": "NASDAQ"}),
            lx.data.Extraction(extraction_class="ticker", extraction_text="STM", attributes={"status": "Hold"}),
            lx.data.Extraction(extraction_class="ticker", extraction_text="TXN", attributes={"status": "Hold"}),

            # Financial Events
            lx.data.Extraction(extraction_class="event", extraction_text="strategic licensing partnership", attributes={"type": "licensing_deal"}),
            lx.data.Extraction(extraction_class="event", extraction_text="integration of key Groq leadership", attributes={"type": "talent_acquisition"}),
            lx.data.Extraction(extraction_class="event", extraction_text="non-exclusive licensing agreement", attributes={"type": "contract_detail"}),

            # Dates
            lx.data.Extraction(extraction_class="timeline", extraction_text="Friday, Dec. 26", attributes={"date_type": "event_date"}),
            lx.data.Extraction(extraction_class="timeline", extraction_text="2025", attributes={"date_type": "fiscal_year"}),
            lx.data.Extraction(extraction_class="timeline", extraction_text="Year to date", attributes={"date_type": "performance_period"}),

            # Financial Figures
            lx.data.Extraction(extraction_class="financial_figure", extraction_text="climbed 1%", attributes={"metric": "daily_gain"}),
            lx.data.Extraction(extraction_class="financial_figure", extraction_text="$190.53", attributes={"metric": "closing_price"}),
            lx.data.Extraction(extraction_class="financial_figure", extraction_text="risen about 42%", attributes={"metric": "YTD_gain"}),
            lx.data.Extraction(extraction_class="financial_figure", extraction_text="-5.7%", attributes={"metric": "peer_performance", "company": "TXN"}),

            # CEO/Leadership Names
            lx.data.Extraction(extraction_class="executive", extraction_text="Groq’s founder", attributes={"role": "joining_leadership"}), # Note: Text says "founder" rather than name in this specific snippet
            
            # Sentiment
            lx.data.Extraction(extraction_class="sentiment", extraction_text="robust gains", attributes={"score": "positive"}),
            lx.data.Extraction(extraction_class="sentiment", extraction_text="continued optimism", attributes={"score": "positive"}),
            lx.data.Extraction(extraction_class="sentiment", extraction_text="concerned about whether AI is actually a bubble", attributes={"score": "neutral_cautionary"}),
            
            # --- RELATIONSHIPS (The Knowledge Graph Edges) ---
            lx.data.Extraction(
                extraction_class="relationship", 
                extraction_text="NVIDIA Corporation’s NVDA stock", 
                attributes={"subject": "NVIDIA Corporation", "predicate": "ISSUES", "object": "NVDA"}
            ),
            lx.data.Extraction(
                extraction_class="relationship", 
                extraction_text="strategic licensing partnership with AI inference chipmaker Groq", 
                attributes={"subject": "NVIDIA Corporation", "predicate": "PARTNERS_WITH", "object": "Groq"}
            ),
            lx.data.Extraction(
                extraction_class="relationship", 
                extraction_text="integration of key Groq leadership into Nvidia’s teams", 
                attributes={"subject": "Groq", "predicate": "PROVIDES_TALENT_TO", "object": "NVIDIA Corporation"}
            ),
            lx.data.Extraction(
                extraction_class="relationship", 
                extraction_text="Nvidia’s shares finished the session at around $190.53", 
                attributes={"subject": "NVDA", "predicate": "HAS_PRICE", "object": "$190.53"}
            ),
            lx.data.Extraction(
                extraction_class="relationship", 
                extraction_text="STMicroelectronics N.V. STM", 
                attributes={"subject": "STMicroelectronics N.V.", "predicate": "ISSUES", "object": "STM"}
            )
        ]
    )
]


# The input text to be processed
sample_text = """"
2025 is now drawing to a close, and U.S. stocks are set to deliver double-digit returns for the third consecutive year. It was a volatile year for the automotive industry, which battled the steep tariffs that President Donald Trump imposed on imports of cars and auto parts. The electric vehicle (EV) industry also faced a setback after the tax credit was withdrawn.

Looking at the price action, General Motors (GM) is outperforming other auto stocks by a wide margin this year. Ford (F), too, is up 34% for the year, and while the gains are lower than GM, they are better than other auto names like Stellantis (STLA), Honda Motor Company (HMC), and Toyota Motors (TM).
More News from Barchart

    This Dividend-Yielding Gold Stock Is Up 184% in 2025. Should You Bet on Higher Gold Prices in 2026?

    Stop Missing Market Moves: Get the FREE Barchart Brief – your midday dose of stock movers, trending sectors, and actionable trade ideas, delivered right to your inbox. Sign Up Now!

www.barchart.com
www.barchart.com

Meanwhile, when it comes to dividends, Ford stands out with its dividend yield of 4.5%, based on a regular quarterly dividend of 15 cents. The actual dividends have been even higher, as Ford has been paying special dividends to help reach its distribution target of between 40% and 50% of annual free cash flows. This year, Ford paid a supplemental dividend of $0.15 to mark the company’s third consecutive special dividend, after dishing out $0.18 last year. Ford paid a special dividend of $0.65 in 2023, after it booked a windfall gain on its investment in electric vehicle startup Rivian (RIVN).
Ford Should End Up Overshooting Its Payout Target in 2025

As things stand today, a supplemental dividend for 2026 is something we can rule out. In fact, looking at Ford’s adjusted free cash flow guidance of between $2 billion and $3 billion, it barely has the money to cover the base dividend at the midpoint. Notably, Ford’s 2025 cash flows took a hit from the fire incident at key supplier Novelis. There was also the tariff impact, which is more of a recurring issue rather than a one-off, unless these are waived.

Looking ahead, Ford’s cash flows would be under pressure over the next couple of years at least. The company announced a massive $19.5 billion charge in its EV business earlier this month. Of this, $5.5 billion would be in cash, which the company expects to incur over the next two years, with the majority coming in 2026.

I believe the best-case scenario for Ford investors would be the company maintaining its current payout, even as that might mean it overshoots the payout targets. Companies cut dividends only in dire scenarios, as was the case in 2020 when both Ford and General Motors suspended their dividends altogether.
GM Prioritized Buybacks Over Dividends

Ideally, Ford should have cut dividends and instead used the free cash to either cut down debt or repurchase shares aggressively, as GM did. Notably, one of the reasons GM outperformed Ford is because of the divergence in their capital allocation strategies. While the Blue Oval has preferred dividends, its Detroit rival has prioritized buybacks, which, as I have said multiple times, made perfect sense given the tepid valuations.

There is the unstated “family element” in Ford’s capital allocation strategy, as the Ford family still owns around 40% of voting powers through Class B shares. The family does not intend to sell its holdings and might prefer a dividend over a buyback, and that’s precisely what has been happening at Ford.
F Stock Forecast

Ford has a consensus rating of “Hold” from the 23 analysts polled by Barchart, while its mean target price of $12.39 is lower than current price levels. Even the Street-high target price of $15 is just about 13% higher.
www.barchart.com
www.barchart.com
Is Ford Stock a Buy for 2026?

I share Wall Street’s pessimism and am not too bullish on Ford heading into 2026, and instead used the recent rise to trim my positions in the stock. Ford has disappointed on multiple fronts, ranging from execution, frequent and frustrating recalls, where it shattered its own decade-old record this year with 152 recalls, and less-than-optimal capital allocation. Ford’s EV strategy has also been literally all over the place, and while I don’t entirely blame the company, given the industry-wide headwinds, the company’s EV performance and strategy leave a lot to be desired.

This divergence between Ford and GM is well-articulated by their price action, where the latter has outperformed the Blue Oval for the second consecutive year. All said, while I don’t see Ford’s prospects as terribly bad for 2026, I would rather bet fresh capital on another name rather than Ford, given the company’s recent record on execution.
"""""


def create_extraction_and_print_results():
# Run the extraction
    result = lx.extract(
    text_or_documents=sample_text,
    prompt_description=prompt,
    examples=examples,
    model_id=model_identifier,
    model_url=local_model_url,
    )

    for extraction in result.extractions:
            if extraction.extraction_text in sample_text and extraction.char_interval is not None:
                print(f"Type: {extraction.extraction_class}")
                print(f"Text: '{extraction.extraction_text}'")
                print(f"Location: chars {extraction.char_interval.start_pos}-{extraction.char_interval.end_pos}")
                print(f"Attributes: {extraction.attributes}")
                print("---")
            else:
                print(f"Type: {extraction.extraction_class}")
                print(f"Text: '{extraction.extraction_text}'")
                #print(f"Location: chars {extraction.char_interval.start_pos}-{extraction.char_interval.end_pos}")
                print(f"Attributes: {extraction.attributes}")

    print("Extraction successful!")

    # Save results to JSONL and generate HTML visualization
    lx.io.save_annotated_documents(
    [result],
    output_name="financial_information_extractions.jsonl",
    output_dir="."
    )

    html_content = lx.visualize("financial_information_extractions.jsonl")

    with open("financial_information_extractions.html", "w") as html_file:
        html_file.write(html_content)


def create_graph_and_visualize(extractions):
    G = nx.DiGraph()

    for extraction in extractions:
        if extraction["extraction_class"] == "relationship":
            subject = extraction["attributes"].get("subject")
            predicate = extraction["attributes"].get("predicate")
            object_ = extraction["attributes"].get("object")
            if subject and predicate and object_:
                G.add_node(subject, type="entity")
                G.add_node(object_, type="entity")
                G.add_edge(subject, object_, label=predicate)

    net = Network(notebook=True)
    net.from_nx(G)
    net.show_buttons(filter_=['physics'])
    net.show("financial_information_graph.html")



def main():
    #create_extraction_and_print_results() /
    with open('financial_information_extractions.jsonl', 'r') as file:
        # Load the JSON data into a Python object
        result = json.load(file)
    create_graph_and_visualize(result['extractions'])
if __name__ == "__main__":

    main()