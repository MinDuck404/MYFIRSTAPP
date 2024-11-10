                # Xử lý câu hỏi trong quest
                    for idx, quest_item in enumerate(quest[::2]):
                        # Loại bỏ ký tự xuống dòng và đặc biệt (chỉ giữ chữ cái, số và khoảng trắng)
                        cleaned_quest_item = re.sub(r'\W+', ' ', quest_item.lower()).strip()
                        cleaned_following_line = re.sub(r'\W+', ' ', following_line.lower()).strip()

                        # So sánh
                        if cleaned_quest_item in cleaned_following_line:
                            answer = quest[idx * 2 + 1].lower()
                            time_delay = q5 if len(answer) < 6 else len(answer) * q6 + 0.456
                            auto(answer, time_delay)
                            break
                    else:
                        print('khong co trong danh sach')