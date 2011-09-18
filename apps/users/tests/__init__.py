# -*- coding: utf-8 -*-

from views.registration import (RegistrationFormTest, ConfirmationFormTest,
    RegistrationViewTest, ConfirmViewTest, ResendViewTest, WelcomeViewTest)
from views.login import LoginViewTest
from views.reset_password import (InitResetPasswordFormTest,
    ResetPasswordFormTest, InitViewTest, ResetPasswordViewTest)
from views.profile import (ProfileViewTest, ProfileEditTest,
    AvatarUpdateViewTest, AvatarDeleteViewTest, GeographyViewTest,
    RolesViewTest, AboutViewTest)
from views.forms import (UserInfoFormTest, ChangePasswordFormTest,
    AvatarFormTest, GeographyFormTest, RolesFormTest, AboutMeFormTest)
