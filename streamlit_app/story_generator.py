from dotenv import load_dotenv

load_dotenv()
# Warning control
import warnings

warnings.filterwarnings("ignore")

from crewai import Agent, Task, Crew, Process
from crewai_tools import tools
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from openai import OpenAI
import os, requests

llm1 = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY")
)
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("GPT_API_KEY"))


def generateimage(chapter_content):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.images.generate(
        model="dall-e-3",
        prompt=f"이미지의 내용: {chapter_content}. Style: Illustration. Create an illustration incorporating a vivid palette with an emphasis on shades of azure and emerald, augmented by splashes of gold for contrast and visual interest. The style should evoke the intricate detail and whimsy of early 20th-century storybook illustrations, blending realism with fantastical elements to create a sense of wonder and enchantment. The composition should be rich in texture, with a soft, luminous lighting that enhances the magical atmosphere. Attention to the interplay of light and shadow will add depth and dimensionality, inviting the viewer to delve into the scene. DON'T include ANY text in this image. DON'T include colour palettes in this image.",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    filename = f"image_{chapter_content[:10].replace(' ', '_')}.png"
    filepath = os.path.join(os.path.dirname(os.getcwd()), "img", filename)

    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open(filepath, "wb") as file:
            file.write(image_response.content)
    else:
        print("Failed to download the image.")
        return ""

    return filepath


story_agent = Agent(
    role="이야기 생성자",
    goal="{theme} 배경으로 흥미로운 상황을 생성합니다.",
    backstory="당신은 유명한 작가입니다."
    "사용자의 요구에 맞게 자연스럽게 흥미로운 이야기를 만들어 낼 수 있습니다."
    "현제 롤플레잉을 하고 있습니다, 이야기를 만들어 나갈 때 주인공의 행동을 당신이 결정해서는 안됩니다. ",
    memory=True,
    allow_delegation=False,
    llm=llm1,
)

# 선택지 에이전트: 상황에 맞는 4가지 선택지를 제공
# 추가로 종료 선택지와, 자유롭게 입력하는 것도 허용
choice_agent = Agent(
    role="선택지 제공자",
    goal="주어진 상황을 보고 주인공이 행동할 선택지를 생성합니다.",
    backstory="당신은 상황에 맞게 선택지를 제시하는 역할을 맡고 있습니다."
    "이야기의 주인공이 당신의 선택지 중 하나를 선택할 것입니다. "
    "선택지를 통해 다른 이야기가 전개될 수 있도록 선택지를 생성하세요. ",
    memory=True,
    allow_delegation=False,
    llm=llm1,
)

# 결말 에이전트
ending_agent = Agent(
    role="이야기 결말 생성자",
    goal="주어진 이야기를 보고 결말을 내립니다.",
    backstory=" 많은 사람이 납득가능하게 이야기를 마무리 할 수 있습니다. ",
    memory=True,
    allow_delegation=False,
    llm=llm1,
)

# 주인공 생성 에이전트
create_player_agent = Agent(
    role="이야기의 주인공 생성자",
    goal="{theme} 배경에 어울리는 인물 한 명을 생성합니다. ",
    backstory="사람에 대해 자새하게 묘사할 수 있습니다.",
    memory=True,
    allow_delegation=False,
    llm=llm1,
)

# 이야기 생성 작업
story_creation_task = Task(
    description=(
        "1. 나열된 규칙을 지키면서 {theme} 배경에 자연스럽고 {previous_story}에 이어지는 새로운 상황을 생성하세요.\n"
        "규칙 1. 주인공의 선택을 마음대로 결정해서는 안됩니다.\n"
        "규칙 2. 주인공이 처한 상황, 다른 인물이 걸어오는 대사 등을 포함합니다.\n"
        "규칙 3. 이야기는 주인공이 어떤 선택을 해야 할 상황에서 끝나도록 하세요.\n"
        "규칙 4. 주인공이 어떤 행동을 할지 질문하거나 궁금해하지 말고, 주인공의 결정을 요구하는 문장 없이 스토리만 생성합니다.\n"
        "규칙 5. 상황을 마무리하는 문장으로 질문이나 선택을 요구하는 문장이 포함되지 않도록 하세요."
    ),
    expected_output=(
        "200글자 내외의 흥미로운 상황이 생성됩니다.\n" "반드시 한국어로 생성하세요."
    ),
    agent=story_agent,
)

# 선택지 생성 작업
# 필요하면 추가 : "선택지는 1.~ 2.~ 3.~ 4.~ 순으로 제공되고 선택지마다 줄바꿈을 해서 출력하세요"
choice_creation_task = Task(
    description="이야기 상황에 맞는 4가지 선택지를 생성하세요. 각 선택지는 이야기와 관련이 있어야 합니다."
    "{previous_story}와 이어지며, 마지막으로 제시된 상황에 맞는 선택지를 생성하세요. \n"
    "5번째 선택지는 고정적으로 '여기서 이야기의 마무리합니다.'입니다.",
    expected_output="상황에 맞는 4가지 선택지가 생성됩니다.\n"
    "모든 선택지 앞에 1. 2. 3. 4. 같이 숫자를 붙이세요\n"
    "각 선텍지는 줄바꿈 하여 출력하세요",
    agent=choice_agent,
)


# 이야기 결말 작업
ending_task = Task(
    description="{previous_story}에 이어지는 결말을 생성하세요"
    "이야기가 마무리되는 느낌으로 되어야 합니다. "
    "'나의 이야기는 이제부터 시작될 것이다.' 등과 같이 새로운 이야기를 암시하는 내용은 포함하지 않습니다. ",
    expected_output="줄글의 형식으로 생성하세요." "반드시 한국어로 생성하세요.",
    agent=ending_agent,
)

# 주인공 생성 작업
create_player_task = Task(
    description="{theme} 배경에 어울리는 인물 한명을 생성합니다. "
    "우선 그 인물의 직업을 5개정도 생성하고 무작위로 하나를 선택합니다. "
    "그 인물의 인적사항을 출력합니다",
    expected_output="당신은 '(직업)'입니다'로 시작해서 인적사항을 적습니다.",
    agent=create_player_agent,
)

story_crew = Crew(
    agents=[
        story_agent,
        choice_agent,
        ending_agent,
        create_player_agent,
        # summerize_agent
    ],
    tasks=[
        story_creation_task,
        choice_creation_task,
        ending_task,
        create_player_task,
        # story_summerization_task
    ],
    process=Process.sequential,
    verbose=True,
)


# 캐릭터 생성함수
def character_creation(crew, theme, storyfile, logfile):
    # 플레이어 생성
    crew.tasks = [create_player_task]
    player_info = crew.kickoff(inputs={"theme": theme, "previous_story": ""})

    # 플레이어 정보가 든 파일 생성
    # 스토리만
    with open(storyfile, "w", encoding="utf-8") as file:
        file.write(f"{player_info}\n\n\n")
    # 스토리와 선택지 포함해서 모든 정보 저장
    with open(logfile, "w", encoding="utf-8") as file:
        file.write(f"{player_info}\n\n\n")

    return player_info


# 이야기 생성 함수
def story_creation(chapter_num, crew, theme, storyfile, logfile):

    # 스토리 파일 읽고 이야기 생성
    with open(storyfile, "r", encoding="utf-8") as file:
        previous_story = file.read()

    crew.tasks = [story_creation_task]
    story_result = crew.kickoff(
        inputs={"theme": theme, "previous_story": previous_story}
    )
    story_text = f"## Chapter{chapter_num} \n{story_result}\n\n"

    # 초기 캐릭터 만들때 파일을 생성해서 그냥 a로
    with open(logfile, "a", encoding="utf-8") as file:
        file.write(story_text)
    with open(storyfile, "a", encoding="utf-8") as file:
        file.write(story_text)
    return story_result


# 선택지 생성 함수
def create_options(crew, theme, storyfile, logfile):

    # 요약 파일 및 방금 생성된 이야기

    with open(storyfile, "r", encoding="utf") as file:
        previous_story = file.read()

    crew.tasks = [choice_creation_task]
    choices_creation = crew.kickoff(
        inputs={"theme": theme, "previous_story": previous_story}
    )
    story_text = f"{choices_creation}\n\n\n"

    # 로그에 저장
    with open(logfile, "a", encoding="utf-8") as file:
        file.write(story_text)

    return choices_creation


# 스트림릿 용 사용자 선택 함수
def user_selection_streamlit(choices_creation, selected_num, storyfile, logfile):

    story_text = f"## 사용자 선택 {selected_num}\n\n\n"

    line = f"{choices_creation}\n\n\n"

    # 로그에 사용자가 선택한 숫자 추가
    with open(logfile, "a", encoding="utf-8") as file:
        file.write(story_text)

    # story.md 에 선택한 내용 추가
    with open(storyfile, "a", encoding="utf-8") as file:
        file.write(line)

    return True


def story_ending(crew, theme, storyfile, logfile):

    with open(storyfile, "r", encoding="utf-8") as file:
        previous_story = file.read()

    # 이야기 생성
    crew.tasks = [ending_task]

    story_result = crew.kickoff(
        inputs={"theme": theme, "previous_story": previous_story}
    )
    story_result_md = f"## 엔딩 \n{story_result}\n\n"

    # 이야기 내용을 파일에 저장
    with open(storyfile, "a", encoding="utf-8") as file:
        file.write(story_result_md)

    # 로그 기록
    with open(logfile, "a", encoding="utf-8") as file:
        file.write(story_result_md)

    return story_result


# def execute_story(
#     crew,
#     theme,
#     logfile="log.md",
#     storyfile="story.md",
#     # summary = 'summary.md',
#     # generated_story = 'generated_story.md'
# ):
#     character_creation(crew,theme,storyfile,logfile)


#     for i in range(9):

#         # 요약을 읽기 / 이야기 생성 / 문장 저장
#         story_result = story_creation(crew, theme, storyfile, logfile)

#         # 이미지 생성 부분 result가 파일 위치
#         # result = generateimage(story_result)

#         # 선택지 생성 / 선택지 내용 저장
#         choices_creation = create_options(crew, theme, storyfile, logfile)

#         # 사용자 선택 / 선택한 내용 저장
#         continue_story = user_selection(choices_creation, storyfile, logfile)
