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
        lead_response: str = None,
        email_subject: str = None,
        email_body: str = None
    ) -> None:
        self.name = name
        self.job_title = job_title
        self.organization = organization
        self.company_size = company_size
        self.department = department
        self.project_title = project_title
        self.looking_for = looking_for
        self.lead_response = lead_response
        self.email_subject = email_subject
        self.email_body = email_body


class OpenerAgent:
    def __init__(self, 
        llm: object, 
        template_path: str,
        leads_path: str,
        model_name: str = 'gpt-3.5-turbo',
        model_temperature: float = 0,
        model_max_tokens: int = 300
    ) -> None:
        self.temperature = model_temperature
        self.model_name = model_name
        self.max_tokens = model_max_tokens
        self.llm = ChatOpenAI(temperature=self.temperature, model_name=self.model_name, max_tokens=self.max_tokens)
        print("Loading template and leads...")
        self.template = self._load_template(template_path)
        print("Opener Template loaded!")
        self.leads = self._load_leads(leads_path)
        print("Opener Leads loaded!")
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
        print("Opener Prompts generated!")


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
                organization=row["Organizaton" if "Organizaton" in row else "Organization"],
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
        print("Opener Generating emails...")
        for i, prompt in enumerate(self.prompts):
            email = self.llm.invoke(prompt)
            data['emails'].append(email)
            data['prompts'].append(prompt)
            data['name'].append(self.leads[i].name)
            data['looking_for'].append(self.leads[i].looking_for)
        print("Opener Emails generated!")
        return data

    
class EscalatorAgent:
    def __init__(self, 
        llm: object, 
        template_path: str,
        leads_path: str,
        opener_path: str,
        model_name: str = 'gpt-3.5-turbo',
        model_temperature: float = 0.2,
        model_max_tokens: int = 300
    ) -> None:
        self.temperature = model_temperature
        self.model_name = model_name
        self.max_tokens = model_max_tokens
        self.llm = llm if llm else ChatOpenAI(temperature=self.temperature, model_name=self.model_name, max_tokens=self.max_tokens)
        print("Escalator Loading template and leads...")
        self.template = self._load_template(template_path)
        print("Escalator Template loaded!")
        self.leads = self._load_leads(leads_path, opener_path)
        print("Escalator Leads loaded!")
        self.replacements = {
            "name": "name",
            "job_title": "job_title",
            "organization": "organization",
            "company_size": "company_size",
            "department": "department",
            "project_title": "project_title",
            "looking_for": "looking_for",
            "lead_response": "lead_response"
        }
        self.prompts = self._make_prompt()
        print("Escalator Prompts generated!")


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


    def _load_leads(self, 
                    path: str,
                    opener_path: str 
                ) -> List[Lead]:
        data = self.read_excel_dynamic(path)
        opener = pd.read_excel(opener_path)
        data.reset_index(inplace=True)
        leads = []
        for i, row in data.iterrows():
            lead = Lead(
                name=row["Name"],
                job_title=row["Job Title"],
                organization=row["Organizaton" if "Organizaton" in row else "Organization"],
                company_size=row["Company Size"],
                department=row["Department"],
                project_title=row["Project Title"],
                looking_for=row["Looking For"],
                lead_response=row["Lead Response"],
                email_subject=opener["Email Subject"][i],
                email_body=opener["Email Body"][i]
            )
            leads.append(lead)
        return leads


    def _load_template(self, path: str) -> str:
        with open(path, 'r') as f:
            return f.read()


    def _make_prompt(self) -> List[tuple]:
        print("Making template...")
        prompts = []
        for lead in self.leads:
            template = self.template
            for key, value in self.replacements.items():
                template = template.replace(f"[{key}]", str(getattr(lead, value)))
            template_split = template.split("#####")
            prompts.append(
                [
                    ("system", template_split[0]),
                    ("human", template_split[1])
                ]
            )
        return prompts
    
    def generate_email(self) -> List[str]:
        data = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "bot_responses": [],
            "prompts": [],
            "name": [],
            "looking_for": [],
            "email_subject": [],
            "email_body": [],
            "lead_response": []
        }
        for i, prompt in enumerate(self.prompts):
            bot_response = self.llm.invoke(prompt)
            data['bot_responses'].append(bot_response)
            data['prompts'].append(prompt)
            data['name'].append(self.leads[i].name)
            data['looking_for'].append(self.leads[i].looking_for)
            data['email_subject'].append(self.leads[i].email_subject)
            data['email_body'].append(self.leads[i].email_body)
            data['lead_response'].append(self.leads[i].lead_response)
        print("Escalator Emails generated!")
        return data

def parse_subject(email: str) -> str:
    return email.split("\n")[0]

def parse_body(email: str) -> str:
    return "\n".join(email.split("\n")[1:])

def opener(
    prompt_path: str = "opener_prompt.md",
    leads_path: str = "leads.xlsx",
    opener_path: str = "opener_output.xlsx",
    model_name: str = 'gpt-3.5-turbo',
    model_temperature: float = 0,
    model_max_tokens: int = 300
    ):
    template_path = prompt_path
    agent = OpenerAgent(llm=None, template_path=template_path, leads_path=leads_path, model_name=model_name, model_temperature=model_temperature, model_max_tokens=model_max_tokens)
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
    p_data.to_excel(opener_path, index=False)
    print("Opener output saved to: ", opener_path)

def escalator(
    prompt_path: str = "escalator_prompt.md",
    leads_path: str = "leads.xlsx",
    opener_path: str = "opener_output.xlsx",
    escalator_path: str = "escalator_output.xlsx",
    model_name: str = 'gpt-3.5-turbo',
    model_temperature: float = 0.2,
    model_max_tokens: int = 300
    ):
    template_path = prompt_path
    agent = EscalatorAgent(llm=None, template_path=template_path, leads_path=leads_path, opener_path=opener_path, model_name=model_name, model_temperature=model_temperature, model_max_tokens=model_max_tokens)
    data = agent.generate_email()
    escalator_df = {
        "Model Name": [],
        "Temperature": [],
        "Name": [],
        "Looking For": [],
        "Prompt": [],
        "Email Subject": [],
        "Email Body": [],
        "Lead Response": [],
        "Lead Status": [],
        "Agent Response": []
    }
    for i in range(len(data['bot_responses'])):
        escalator_df["Model Name"].append(data['model_name'])
        escalator_df["Temperature"].append(data['temperature'])
        escalator_df["Name"].append(data['name'][i])
        escalator_df["Looking For"].append(data['looking_for'][i])
        escalator_df["Prompt"].append(data['prompts'][i])
        escalator_df["Email Subject"].append(data['email_subject'][i])
        escalator_df["Email Body"].append(data['email_body'][i])
        escalator_df["Lead Response"].append(data['lead_response'][i])
        escalator_df["Lead Status"].append("Escalated" if "Escalated" in data["bot_responses"][i].content else "Not Escalated")
        escalator_df["Agent Response"].append("NULL" if "Escalated" in data["bot_responses"][i].content else data["bot_responses"][i].content)
    
    e_data = pd.DataFrame(escalator_df)
    e_data.to_excel(escalator_path, index=False)
    
        

# if __name__ == "__main__":
#     main()
#     escalator()
