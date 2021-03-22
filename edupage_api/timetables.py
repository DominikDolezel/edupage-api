import datetime, json


class EduLesson:
    def __init__(self, name, subject_id, teacher, classroom, length):
        self.name = name
        self.teacher = teacher
        self.classroom = classroom
        self.length = length
        self.subject_id = subject_id

    def __str__(self):
        return str(self.__dict__)


class EduOnlineLesson(EduLesson):
    def __init__(self, name, subject_id, teacher, classroom, length,
                 online_lesson_link):
        super().__init__(name, subject_id, teacher, classroom, length)
        self.online_lesson_link = online_lesson_link

    # Tell edupage that you are on this online lesson
    def sign_into_lesson(self, edupage):
        request_url = "https://" + edupage.school + ".edupage.org/dashboard/eb.php"

        response = edupage.session.get(request_url)

        # we will need this for the next request
        gse_hash = response.content.decode() \
                                        .split("gsechash=")[1] \
                                        .split('"')[1]  # I have no idea what this is, but it can be easily parsed

        request_url = "https://" + edupage.school + ".edupage.org/dashboard/server/onlinelesson.js?__func=getOnlineLessonOpenUrl"

        today = datetime.datetime.now()
        post_data = {
            "__args": [  # wtf is this name
                None,  # The first element is always null???
                {
                    "click": True,
                    "date": today.strftime("%Y-%m-%d"),
                    "ol_url": self.online_lesson_link,
                    "subjectid": self.subject_id
                }
            ],
            "__gsh":
            gse_hash
        }

        response = edupage.session.post(request_url, json=post_data)
        # if reload is True, request failed: the gsh hash was wrong:(
        return json.loads(response.content.decode()).get("reload") == None


class EduTimetable:
    def __init__(self, lessons):
        self.lessons = lessons

    def get_lesson_at_time(self, edutime):
        for lesson in self.lessons:
            if lesson.length.start.is_after_or_equals(
                    edutime) and lesson.length.end.is_before_or_equals(
                        edutime):
                return lesson

        return None

    def get_next_lesson_at_time(self, edutime):
        previous = None
        for lesson in self.lessons:
            if previous == None:
                if lesson.start.is_before(edutime):
                    return lesson
            else:
                if lesson.start.is_before(edutime) and previous.end.is_after(
                        edutime):
                    return lesson

            previous = lesson

        return None

    def get_first_lesson(self):
        return self.lessons[0]

    def get_last_lesson(self):
        return self.lessons[-1]
