import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + ",\n" + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"Title: {self.title} |\t Course: {self.course.name}"

    


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


# <HINT> Create a Question Model with:
    # Used to persist question content for a course
    # Has a One-To-Many (or Many-To-Many if you want to reuse questions) relationship with course
    # Has a grade point for each question
    # Has question content
    # Other fields and methods you would like to design

class Question(models.Model):
    
    # Foreign key to lesson
    # question text
    # question grade/mark

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question_text = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        default="Question"
    )
    grade = models.IntegerField(
        null=False,
        blank=False,
        default=1
    )

    def __str__(self):
        return "Lesson: {}, Question: {}, Grade: {}".format(
            self.lesson.pk,
            self.question_text,
            self.grade
        )
    

    # <HINT> A sample model method to calculate if learner get the score of the question
    #def is_get_score(self, selected_ids):
    #    all_answers = self.choice_set.filter(is_correct=True).count()
    #    selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
    #    if all_answers == selected_correct:
    #        return True
    #    else:
    #        return False
    def get_score(self, selected):
        choices = self.choice_set.all()
        selected_count = selected.filter(question__id=self.id,is_correct=True).count()
        total_items = choices.count()
        correct = 0
        if selected_count > 0:
            for choice in choices:
                if choice.is_correct == True and choice in selected:
                    correct += 1
                elif choice.is_correct == False and choice not in selected:
                    correct += 1
        percentage = correct / total_items
        points = percentage * self.grade
        print("###### Q{} {}/{} = {}, {}/{}".format(self.id, correct, total_items, percentage, points, self.grade))
        return points, self.grade


#  <HINT> Create a Choice Model with:
    # Used to persist choice content for a question
    # One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
    # Choice content
    # Indicate if this choice of the question is a correct one or not
    # Other fields and methods you would like to design
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        default="Choice *"
    )
    is_correct = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return "choice_text: {0}, Question: {2}, is_correct: {1}".format(
            self.choice_text,
            self.is_correct,
            self.question.question_text,
        )


# <HINT> The submission model
# One enrollment could have multiple submission
# One submission could have multiple choices
# One choice could belong to multiple submissions
#class Submission(models.Model):
#    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
#    chocies = models.ManyToManyField(Choice)
#    Other fields and methods you would like to design
class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    def __str__(self):
        return "Enrollment: {}, Choices: {}".format(self.enrollment.mode, len(self.choices))
    