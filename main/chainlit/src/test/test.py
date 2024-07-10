from actors import LlmInterviewer, HumanInterviewee

interviewer = LlmInterviewer("interviewer", "gpt-4-32k")
interviewee = HumanInterviewee("Yuichiro", "Yuichiro Noguchi", "yuichiro.noguchi@apol.co.jp")

print(interviewer.role)
print(interviewer.handleName)
print(interviewer.modelName)

print(interviewee.role)
print(interviewee.handleName)
print(interviewee.userName)
print(interviewee.emailAddress)