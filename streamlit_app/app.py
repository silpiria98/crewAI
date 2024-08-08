import streamlit as st
import story_generator
import re,os
import image_generator

st.set_page_config(
    page_title="아이펠 던전 AI"
)

if "page" not in st.session_state:  # 초기 상태 설정
    st.session_state.page = "page1"

if st.session_state.page == "page1":  #첫 화면
    with st.container():
        # 타이틀
        st.title("AIFFEL 던전 AI")

        st.image("images/dragon.jpg", caption="", use_column_width=True)
        # 게임 설명
        st.subheader( "선택의 기로에서 마주하는 수많은 갈림길 \n 당신의 결정이 이야기의 향방을 바꿉니다. 신중하게 선택하고, 그 결과를 마주하세요.")

        st.write("")

        def movetopage2():
            st.session_state.page = "page2"
        st.button("GAME START!", key="gamestart", on_click=movetopage2)
           
        
elif st.session_state.page == "page2":  # 컨테이너 숨김 상태일 때
    # 컨테이너가 사라진 후에 표시할 내용 (예: 게임 화면)
    st.subheader("원하시는 모험의 테마를 입력해주세요!")
    col1, col2 = st.columns([1,1])

    if "theme" not in st.session_state:
        st.session_state.theme = ""  # 초기값 설정

    with col1:
        theme = st.text_input("",placeholder="예: 어둠 속의 미궁, 고대 유적 탐험")
        
    if st.button("NEXT",key="nextfrom2page"):
        if theme.strip() == "":  # 입력값이 비어있거나 공백만 있는 경우
            st.warning("테마를 입력해주세요!")  # 경고 메시지 표시
        else:
            st.session_state.page = "page3"
            st.session_state.theme = theme #테마 입력값 유지
            st.rerun()
        
elif st.session_state.page == "page3":
    st.title("캐릭터 소개")
    st.caption(f"선택된 테마 : {st.session_state.theme}")


    #플레이어 정보 state
    if "player_information" not in st.session_state:  
        st.session_state.player_information = ""
    
    if "player_info_count" not in st.session_state:  
        st.session_state.player_info_count = 0

    if st.session_state.player_info_count == 0:
        player_info = story_generator.character_creation(story_generator.story_crew,
                                                        st.session_state.theme,
                                                        "story.md",
                                                        "log.md",)
        st.session_state.player_info_count += 1
        st.session_state.player_information = player_info
    
        st.write(st.session_state.player_information)

    def movetopage4():
        st.session_state.page = "page4"
    st.button("NEXT",key="pagefrom3page",on_click=movetopage4)
                

elif st.session_state.page == "page4":
     # 상황 count
    if "count_scene" not in st.session_state:
            st.session_state.count_scene = 1

    if st.session_state.count_scene == 8: #7회까지만 진행 후 엔딩
            st.session_state.page = "page5"
            st.session_state.show_story = False
            st.rerun()  

    if "show_story" not in st.session_state:
        st.session_state.show_story = True

    if st.session_state.show_story:   #테마가 rerun 되었을때
        st.caption(f"선택된 테마 : {st.session_state.theme}")

        
        st.text(f"#상황. {st.session_state.count_scene}")
        
            
        # 생성된 글 저장 
        if "created_story" not in st.session_state:  
            st.session_state.created_story = ""
        
        created_story = story_generator.story_creation(st.session_state.count_scene,
                                                       story_generator.story_crew, 
                                                        st.session_state.theme, 
                                                        "story.md",
                                                        "log.md")
        
        st.session_state.count_scene += 1

        st.session_state.created_story = created_story

        st.write(created_story) #스토리 화면
        
        st.text("")
    
        # 선택지 생성
        choices_creation = story_generator.create_options(story_generator.story_crew, 
                                                            st.session_state.theme, 
                                                            "story.md",
                                                            "log.md")
        #선택된 선택지 선택
        if "option_selected" not in st.session_state:  
            st.session_state.option_selected = ""
        if "option_selected_num" not in st.session_state:  
            st.session_state.option_selected_num = 0

        choices_lines = choices_creation.split("\n")

        choices_lines = [sentence for sentence in choices_lines if re.match(r"^[1-5]\.", sentence)] #선택지 배열 
            
            
        #선택지 1
        def selectedinfo(selected_line, num):
            story_generator.user_selection_streamlit(selected_line, 
                                                     num,
                                                     "story.md", 
                                                     "log.md") #사용자가 선택한 정보를 기록

        st.button(choices_lines[0], key=0, on_click=lambda: selectedinfo(choices_lines[0], 0))
        st.button(choices_lines[1], key=1, on_click=lambda: selectedinfo(choices_lines[1], 1))
        st.button(choices_lines[2], key=2, on_click=lambda: selectedinfo(choices_lines[2], 2))
        st.button(choices_lines[3], key=3, on_click=lambda: selectedinfo(choices_lines[3], 3))
    
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.button("직접 선택지 작성 하기",key=4)

        #선택지 5
        with col3:
            def nextpage_clicked_onpage4():
                st.session_state.page = "page5"
                st.session_state.show_story = False
            
            st.button("엔딩 보기",key=5,on_click=nextpage_clicked_onpage4)
                

elif st.session_state.page == "page5":
    if "show_ending" not in st.session_state:  
            st.session_state.show_ending = True

    if st.session_state.show_ending:
        st.caption(f"선택된 테마 : {st.session_state.theme}")
        st.text(f"#엔딩..")
        
        ending_story = story_generator.story_ending(story_generator.story_crew, 
                                                    st.session_state.theme, 
                                                    "story.md",
                                                    "log.md")
        st.write(ending_story)
        if "generated_image_path" not in st.session_state:  
            st.session_state.generated_image_path = ""
        st.session_state.generated_image_path= image_generator.generateimage(ending_story,"story.md")
        #사용자 선택 / 선택한 내용 저장
        def nextpage_clicked_onpage5():
            st.session_state.page = "page6"
            st.session_state.show_ending = False
        
        st.button("모험기록 보기",key="pagefrom6page",on_click= nextpage_clicked_onpage5)
                    
        
            

elif st.session_state.page == "page6":
    st.title("당신의 모험 기록")
    st.caption(f"선택된 테마 : {st.session_state.theme}")
    st.text("")

    with open("story.md", "r", encoding="utf-8") as f:
      log_content = f.read()
    
    # Streamlit에 출력
    st.markdown(log_content, unsafe_allow_html=True)
    st.image(st.session_state.generated_image_path, caption="", use_column_width=True)