from bs4 import BeautifulSoup

def extract_body_only(html_cont):
    soup = BeautifulSoup(html_cont,"lxml")
    body_cont = soup.body

    if body_cont:
        return str(body_cont)

    else:
        return ""
    

def clean_body(body_cont):
    soup = BeautifulSoup(body_cont,"lxml")


    for script_style in soup(["script", "style", "nav", "header", "footer"]):
        script_style.extract()

    cleaned_content = soup.get_text(separator="\n")

    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())

    return cleaned_content


def split_dom_content(dom_content , maxlength = 6000):
    return [
        dom_content[i:i + maxlength] for i in range (0 ,len(dom_content) , maxlength)
    ]
