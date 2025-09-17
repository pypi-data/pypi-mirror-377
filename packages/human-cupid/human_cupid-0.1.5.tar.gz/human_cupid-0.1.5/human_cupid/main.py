from human_cupid.cupid import Cupid
from human_cupid.sub import SubprofileAnalyzer
from human_cupid.super import SuperprofileAnalyzer

Alex_Mom = [
    {"sender": "alex", "content": "hey mom, just wanted to check in"},
    {"sender": "mom", "content": "Hi honey! How are you feeling today?"},
    {"sender": "alex", "content": "honestly pretty stressed about work stuff"},
    {"sender": "mom", "content": "What's going on? You can tell me"},
    {"sender": "alex", "content": "my manager keeps piling on coding projects and I don't want to disappoint anyone"},
    {"sender": "mom", "content": "You're such a hard worker, but don't forget to take care of yourself"},
    {"sender": "alex", "content": "I know, I know. just want to make you proud"},
    {"sender": "mom", "content": "I'm already proud of you! Always remember that"},
    {"sender": "alex", "content": "thanks mom ❤️ that helps"},
    {"sender": "mom", "content": "Have you been eating enough? And sleeping?"},
    {"sender": "alex", "content": "um... define enough? 😅"},
    {"sender": "mom", "content": "Alex! You need to take better care of yourself"},
    {"sender": "alex", "content": "okay okay I'll try to do better. promise"},
    {"sender": "mom", "content": "Good. I worry about you working so hard"},
    {"sender": "alex", "content": "I appreciate you caring so much"},
    {"sender": "mom", "content": "That's what mothers are for"},
    {"sender": "alex", "content": "speaking of which, how's dad doing?"},
    {"sender": "mom", "content": "He's good! Still complaining about his back though"},
    {"sender": "alex", "content": "tell him to actually do the physical therapy exercises lol"},
    {"sender": "mom", "content": "I've been trying! He's as stubborn as you"},
    {"sender": "alex", "content": "hey! I'm not stubborn, I'm... persistent 😏"},
    {"sender": "mom", "content": "Uh huh, sure honey"},
    {"sender": "alex", "content": "anyway I should probably get back to work"},
    {"sender": "mom", "content": "Okay, but remember what we talked about - take breaks!"},
    {"sender": "alex", "content": "will do. love you mom"},
    {"sender": "mom", "content": "Love you too sweetie. Talk soon!"}
]

def main():
    with open("alex_mom_profile.json", "r") as f:
        alex_mom_profile = f.read()
        a = SubprofileAnalyzer("alex", Alex_Mom, alex_mom_profile).run()

        print(a)
        
        # save to alex_mom_subprofile.json
        if a:
            with open("alex_mom_subprofile.json", "w") as f:
                f.write(a.model_dump_json(indent=2))