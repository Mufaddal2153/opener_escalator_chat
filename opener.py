from typing import Dict, List
import pandas as pd, os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class Lead:
    def __init__(
        self, name: str,
        job_title: str,
        organization: str,
        company_size: str,
        department: str,
        project_title: str,
        looking_for: str,
        lead_response: str = None
    ) -> None:
        self.name = name
        self.job_title = job_title
        self.organization = organization
        self.company_size = company_size
        self.department = department
        self.project_title = project_title
        self.looking_for = looking_for
        self.lead_response = None


class OpenerAgent:
    def __init__(self, 
        llm: object, 
        template_path: str,
        leads_path: str
    ) -> None:
        self.temperature = 0
        self.model_name = 'gpt-3.5-turbo'
        self.max_tokens = 300
        self.llm = ChatOpenAI(temperature=self.temperature, model_name=self.model_name, max_tokens=self.max_tokens)
        self.template = self._load_template(template_path)
        self.leads = self._load_leads(leads_path)
        self.replacements = {
            "name": "name",
            "job_title": "job_title",
            "organization": "organization",
            "company_size": "company_size",
            "department": "department",
            "project_title": "project_title",
            "looking_for": "looking_for"
        }
        self.prompts = self._make_prompt()


    def read_excel_dynamic(self, path: str) -> pd.DataFrame:
        df = pd.read_excel(path)
        non_empty_row = next((i for i, row in df.iterrows() if not row.isnull().all()), None)
        if non_empty_row is not None:
            df.columns = df.iloc[non_empty_row]
            df = df.iloc[non_empty_row+1:]
            non_empty_col = df.notna().any(axis=0)
            df = df.loc[:, non_empty_col]
        else:
            print("Excel file seems to be empty!")
            df = pd.DataFrame()
        return df


    def _load_leads(self, path: str) -> List[Lead]:
        data = self.read_excel_dynamic(path)
        leads = []
        for i, row in data.iterrows():
            lead = Lead(
                name=row["Name"],
                job_title=row["Job Title"],
                organization=row["Organizaton"],
                company_size=row["Company Size"],
                department=row["Department"],
                project_title=row["Project Title"],
                looking_for=row["Looking For"]
            )
            leads.append(lead)
        return leads


    def _load_template(self, path: str) -> str:
        with open(path, 'r') as f:
            return f.read()


    def _make_prompt(self) -> PromptTemplate:
        print("Making template...")
        prompts = []
        for lead in self.leads:
            template = self.template
            for key, value in self.replacements.items():
                template = template.replace(f"[{key}]", str(getattr(lead, value)))
            prompts.append(
                [
                    ("system", template)
                ]
            )
        return prompts


    def generate_email(self) -> List[str]:
        emails = []
        data = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "emails": [],
            "prompts": [],
            "name": [],
            "looking_for": []
        }
        for i, prompt in enumerate(self.prompts):
            email = self.llm.invoke(prompt)
            data['emails'].append(email)
            data['prompts'].append(prompt)
            data['name'].append(self.leads[i].name)
            data['looking_for'].append(self.leads[i].looking_for)
        return data

def parse_subject(email: str) -> str:
    return email.split("\n")[0]

def parse_body(email: str) -> str:
    return "\n".join(email.split("\n")[1:])

def main():
    template_path = "opener_prompt.md"
    agent = OpenerAgent(llm=None, template_path=template_path, leads_path="leads.xlsx")
    data = agent.generate_email()
    opener_df = {
        "Model Name": [],
        "Temperature": [],
        "Name": [],
        "Looking For": [],
        "Prompt": [],
        "Email Subject": [],
        "Email Body": [],
    }
    for i in range(len(data['emails'])):
        opener_df["Model Name"].append(data['model_name'])
        opener_df["Temperature"].append(data['temperature'])
        opener_df["Name"].append(data['name'][i])
        opener_df["Looking For"].append(data['looking_for'][i])
        opener_df["Prompt"].append(data['prompts'][i])
        opener_df["Email Subject"].append(parse_subject(data['emails'][i].content))
        opener_df["Email Body"].append(parse_body(data['emails'][i].content))
    p_data = pd.DataFrame(opener_df)
    p_data.to_excel("opener_output.xlsx", index=False)

    print(p_data)


if __name__ == "__main__":
    main()
