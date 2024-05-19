import pytest
from flask import url_for
from playwright.sync_api import expect, Page


def test_load_home_page(app, client, page: Page):
    page.goto("http://127.0.0.1:5000/UKUP/competence")
    page.get_by_role("button", name="Добавить").click()
    page.locator("#type").select_option("ОПК")
    page.locator("#module").click()
    page.locator("#module").fill("Описание")
    page.locator("#type").select_option("УК")
    page.get_by_role("button", name="Submit").click()
    
    expect(page.locator('table')).to_contain_text("ОПК")
    expect(page.locator('body')).to_contain_text("Описание")


def test_add_indicators(app, client, page: Page):
    page.goto("http://127.0.0.1:5000/UKUP/competence")
    page.get_by_role("button", name="Компетенции").click()
    page.get_by_role("button", name="Добавить").click()
    page.locator("#num").click()
    page.locator("#num").click()
    page.locator("#module").click()
    page.locator("#module").fill("")
    page.locator("#module").press("CapsLock")
    page.locator("#module").fill("О")
    page.locator("#module").press("CapsLock")
    page.locator("#module").fill("Описание")
    page.get_by_role("button", name="Submit").click()
    page.get_by_alt_text("Редактировать").click()
    page.get_by_role("button", name="+").click()
    page.get_by_role("textbox").nth(3).click()
    page.get_by_role("textbox").nth(3).press("CapsLock")
    page.get_by_role("textbox").nth(3).fill("И")
    page.get_by_role("textbox").nth(3).press("CapsLock")
    page.get_by_role("textbox").nth(3).fill("Индикатор 1")
    page.get_by_role("textbox").nth(3).press("Enter")
    page.get_by_alt_text("Редактировать").click()

    expect(page.locator('body')).to_contain_text("Индикатор 1")


def test_add_delete_discipline(app, client, page: Page):
    page.goto("http://127.0.0.1:5000/UKUP/competence")
    page.locator("#sidebar").get_by_role("button", name="Дисциплины").click()
    page.get_by_role("button", name="Добавить").click()
    page.locator("#name").click()
    page.locator("#name").press("CapsLock")
    page.locator("#name").fill("L")
    page.locator("#name").press("CapsLock")
    page.locator("#name").fill("")
    page.locator("#name").press("CapsLock")
    page.locator("#name").fill("Д")
    page.locator("#name").press("CapsLock")
    page.locator("#name").fill("Дисциплина")
    page.get_by_role("button", name="Submit").click()

    expect(page.locator('body')).to_contain_text("Дисциплина")
    expect(page.locator('body')).to_contain_text("Б1.Б")
    expect(page.locator('body')).to_contain_text("ИМО")

    page.get_by_alt_text("Редактировать").click()
    page.locator("#name").click()
    page.locator("#name").fill("Дисциплина 1")
    page.locator("#block").select_option("2")
    page.locator("#module").select_option("2")
    page.locator("#department").select_option("2")
    page.get_by_role("button", name="Submit").click()

    expect(page.locator('body')).to_contain_text("Дисциплина 1")
    expect(page.locator('body')).to_contain_text("Б1.В.ВД")
    expect(page.locator('body')).to_contain_text("ПМиК")

    page.get_by_alt_text("Удалить").click()

    expect(page.locator('body')).not_to_contain_text("Дисциплина")
    expect(page.locator('body')).not_to_contain_text("Б1.Б")
    expect(page.locator('body')).not_to_contain_text("ИМО")


def test_create_discipline_links(app, client, page: Page):
    page.goto("http://127.0.0.1:5000/UKUP/competence")
    page.locator("#sidebar").get_by_role("button", name="Дисциплины").click()
    page.get_by_role("cell", name="Компетенции").locator("input[type=\"submit\"]").click()
    page.locator("#connect-30").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("cell", name="Компетенции").locator("input[type=\"submit\"]").click()

    expect(page.locator("#connect-30")).to_be_checked()

    page.locator("#connect-30").uncheck()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("cell", name="Компетенции").locator("input[type=\"submit\"]").click()

    expect(page.locator("#connect-30")).not_to_be_checked()


def test_create_discipline_indicator_links(app, client, page: Page):
    page.goto("http://127.0.0.1:5000/UKUP/competence")
    page.get_by_role("button", name="Компетенции").click()
    page.get_by_role("cell", name="Дисциплины").locator("input[type=\"submit\"]").click()
    page.locator("#connect-1").check()
    page.get_by_role("button", name="Спаси и сохрани").click()
    page.get_by_role("cell", name="Дисциплины").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()
    page.locator("[id=\"\\32 -1\"]").check()
    page.locator("[id=\"\\31 -1\"]").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("cell", name="Компетенции").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()

    expect(page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\33 \"]")).to_be_checked()
    expect(page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\32 \"]")).to_be_checked()

    page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\33 \"]").uncheck()
    page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\32 \"]").uncheck()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("cell", name="Компетенции").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()

    expect(page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\33 \"]")).not_to_be_checked()
    expect(page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\32 \"]")).not_to_be_checked()


def test_create_report(app, client, page: Page):
    page.goto("http://127.0.0.1:5000/UKUP/competence")
    page.get_by_role("button", name="Добавить").click()
    page.locator("#module").click()
    page.locator("#module").fill("ыфафыафа")
    page.get_by_role("button", name="Submit").click()
    page.locator("#sidebar").get_by_role("button", name="Дисциплины").click()
    page.get_by_role("button", name="Добавить").click()
    page.locator("#name").click()
    page.locator("#name").fill("фвыфвф")
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("button", name="Добавить").click()
    page.locator("#name").click()
    page.locator("#name").fill("ыыыыыыыыыыыыыыыыы")
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("row", name="3 ыыыыыыыыыыыыыыыыы Б1").locator("input[type=\"submit\"]").click()
    page.locator("#connect-31").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("row", name="фвыфвф Б1.Б ИМО Компетенции").locator("input[type=\"submit\"]").click()
    page.locator("#connect-30").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("row", name="ыфвфыв Б1.Б ИМО Компетенции").locator("input[type=\"submit\"]").click()
    page.locator("#connect-31").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("row", name="ыфвфыв Б1.Б ИМО Компетенции").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()
    page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\32 \"]").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("row", name="фвыфвф Б1.Б ИМО Компетенции").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()
    page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\33 \"]").check()
    page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\33 \"]").uncheck()
    page.locator("form").filter(has_text="ПК-1 - Описание ПК-1.1").locator("[id=\"\\33 \"]").check()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("row", name="фвыфвф Б1.Б ИМО Компетенции").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()
    page.goto("http://127.0.0.1:5000/UKUP/discipline?year=2024&direction=1")

    expect(page.locator("body")).to_contain_text("ыфвфыв")
    expect(page.locator("body")).to_contain_text("фвыфвф")
    expect(page.locator("body")).to_contain_text("ыыыыыыыыыыыыыыыыы")
    expect(page.locator("body")).to_contain_text("УК-1")
    expect(page.locator("body")).to_contain_text("ПК-1")
    expect(page.locator("body")).to_contain_text("Индикатор 1")
    expect(page.locator("body")).to_contain_text("фывфы")
    expect(page.locator("body")).to_contain_text("фывфыв")

    page.get_by_role("row", name="3 ыыыыыыыыыыыыыыыыы Б1").locator("input[type=\"submit\"]").click()
    page.get_by_role("button", name="Индикаторы").click()
    page.get_by_role("button", name="Подтвердить").click()
    page.get_by_role("link", name="Матрица").click()
    page.goto("http://127.0.0.1:5000/UKUP/discipline?year=2024&direction=1")
    page.get_by_role("link", name="Компетенции").click()

    expect(page.locator("body")).to_contain_text("УК-1")
    expect(page.locator("body")).to_contain_text("ПК-1")